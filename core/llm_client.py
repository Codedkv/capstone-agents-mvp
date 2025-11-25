import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import json

class GeminiClient:
    def __init__(self, api_key=None, model="gemini-2.5-flash"):
        """
        Initialize Gemini client with correct model name.
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

    async def call(self, prompt, tools=None, system_instruction=None, max_retries=3):
        """
        Async Gemini call with function calling loop!
        If the LLM requests a function_call, it will be executed and the result will be returned to the LLM.
        Returns the final response with resolved tool calls.
        """
        if system_instruction:
            prompt = f"{system_instruction}\n{prompt}"

        retries = 0
        last_tool_response = None
        # Build the request contents for the LLM (can append tool response in the next turn)
        contents = [prompt]
        while retries < max_retries:
            try:
                # If there was a tool response previously, pass as proper function_response for LLM
                if last_tool_response:
                    # ADK/Gemini expects a dict like this for a tool result
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

                # Check if the response contains a function call
                if response.candidates and response.candidates[0].content.parts:
                    first_part = response.candidates[0].content.parts[0]
                    if hasattr(first_part, "function_call") and first_part.function_call:
                        # Get function name and arguments
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
                        last_tool_response = {"name": func_name, "response": tool_result}
                        # Continue the loop so LLM can use the tool result properly
                        continue

                # If a regular completion is reached — return output text
                return response.text if hasattr(response, "text") else str(response)

            except Exception as e:
                retries += 1
                print(f"[GeminiClient] Error on attempt {retries}/{max_retries}: {e}")
                if retries >= max_retries:
                    raise e
        return None
