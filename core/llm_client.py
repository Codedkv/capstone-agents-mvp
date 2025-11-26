import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import json
from core.rate_limiter import RateLimiter


class GeminiClient:
    def __init__(self, api_key=None, model="gemini-2.5-flash"):
        """
        Initialize Gemini client with correct model name and rate limiting.
        """
        self.api_key = (
            api_key
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY in .env file."
            )

        print(f"[GeminiClient] API Key loaded: {self.api_key[:10]}...")
        self.model_name = model
        print(f"[GeminiClient] Using model: {self.model_name}")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.rate_limiter = RateLimiter()

    async def call(self, prompt, tools=None, system_instruction=None, max_retries=3):
        """
        Async Gemini call with function calling loop, safety handling, and rate limiting.
        If the LLM requests a function_call, it will be executed and the result will be returned to the LLM.
        Returns the final response with resolved tool calls.
        """
        if system_instruction:
            prompt = f"{system_instruction}\n{prompt}"

        # Rate limiting: estimate tokens and wait if needed
        estimated_tokens = len(prompt.split()) * 2
        await self.rate_limiter.wait_if_needed(estimated_tokens=estimated_tokens)

        retries = 0
        last_tool_response = None
        contents = [prompt]
        
        while retries < max_retries:
            try:
                # If there was a tool response previously, pass as proper function_response for LLM
                if last_tool_response:
                    function_response = {
                        "function_response": {
                            "name": last_tool_response["name"],
                            "response": last_tool_response["response"]
                        }
                    }
                    contents.append(function_response)

                response = await self.model.generate_content_async(
                    contents,
                    tools=tools if tools else None
                )

                # Check for safety blocks or empty responses
                if not response.candidates:
                    print("[GeminiClient] Warning: No candidates returned (blocked by safety filters)")
                    return "Error: Response blocked by safety filters or no candidates returned."
                
                candidate = response.candidates[0]
                
                # Check finish_reason for safety blocks
                if candidate.finish_reason == 2:  # SAFETY
                    print("[GeminiClient] Warning: Response blocked by safety filters (finish_reason=2)")
                    return "Error: Response blocked by Gemini safety filters. Try rephrasing the prompt or adjusting safety settings."
                
                if candidate.finish_reason == 3:  # RECITATION
                    print("[GeminiClient] Warning: Response blocked due to recitation (finish_reason=3)")
                    return "Error: Response blocked due to recitation. Content may be copyrighted."
                
                if candidate.finish_reason == 4:  # OTHER
                    print("[GeminiClient] Warning: Response blocked for unknown reason (finish_reason=4)")
                    return "Error: Response blocked for unknown reason. Please try again."

                # Check if the response contains a function call
                if candidate.content.parts:
                    first_part = candidate.content.parts[0]
                    
                    # Handle function call
                    if hasattr(first_part, "function_call") and first_part.function_call:
                        func_name = first_part.function_call.name
                        func_args = {
                            k: v for k, v in first_part.function_call.args.items()
                        }
                        
                        # Find the function object among tools
                        func_obj = None
                        if tools:
                            for t in tools:
                                if t.__name__ == func_name:
                                    func_obj = t
                                    break
                        
                        if func_obj is None:
                            raise ValueError(f"Function {func_name} not found in tools.")
                        
                        print(f"[GeminiClient] Executing tool: {func_name}({func_args})")
                        
                        # Call the function — result is passed in special function_response format for LLM
                        tool_result = func_obj(**func_args)
                        if not isinstance(tool_result, dict):
                            tool_result = {"result": tool_result}
                        
                        last_tool_response = {"name": func_name, "response": tool_result}
                        # Continue the loop so LLM can use the tool result properly
                        continue
                    
                    # Handle text response
                    if hasattr(first_part, "text") and first_part.text:
                        return first_part.text

                # Fallback: try to extract text from response
                if hasattr(response, "text"):
                    return response.text
                
                # If no text available, return string representation
                print("[GeminiClient] Warning: No text in response, returning string representation")
                return str(response)

            except Exception as e:
                retries += 1
                error_msg = str(e)
                print(f"[GeminiClient] Error on attempt {retries}/{max_retries}: {error_msg}")
                
                # Check if it's a quota error (429)
                if "429" in error_msg or "quota" in error_msg.lower():
                    print("[GeminiClient] Quota exceeded. Rate limiter will wait before next attempt.")
                    import asyncio
                    await asyncio.sleep(10)  # Wait 10 seconds on quota errors
                
                if retries >= max_retries:
                    raise e
        
        return "Error: Max retries exceeded without successful response."
