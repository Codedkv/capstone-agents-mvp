import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key=None, model="gemini-2.5-flash"):
        """
        Initialize Gemini client with correct model name.
        Default model: gemini-2.5-flash (best price/performance for agentic apps)
        Alternative: gemini-2.5-pro (advanced reasoning, more expensive)
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
        Make async call to Gemini API with optional function calling.
        Handles both text responses and function calls.
        """
        if system_instruction:
            prompt = f"{system_instruction}\n{prompt}"

        retries = 0
        while retries < max_retries:
            try:
                if tools:
                    response = await self.model.generate_content_async(
                        prompt,
                        tools=tools,
                    )
                else:
                    response = await self.model.generate_content_async(
                        prompt
                    )
                
                if not response:
                    return None
                
                # Check if response contains function calls
                if response.candidates and response.candidates[0].content.parts:
                    first_part = response.candidates[0].content.parts[0]
                    
                    # If it's a function call, return the structured call info
                    if hasattr(first_part, 'function_call') and first_part.function_call:
                        return {
                            'type': 'function_call',
                            'function_call': first_part.function_call
                        }
                
                # Otherwise return text
                return response.text if hasattr(response, 'text') else str(response)
                
            except Exception as e:
                retries += 1
                print(f"[GeminiClient] Error on attempt {retries}/{max_retries}: {e}")
                if retries >= max_retries:
                    raise e
        return None
