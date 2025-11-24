import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key=None, model="gemini-pro"):
        # Импорт ключа из .env (работает и с GOOGLE_API_KEY, и с GEMINI_API_KEY)
        self.api_key = (
            api_key
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )
        print("Gemini API Key loaded:", self.api_key)  # диагностика
        # Используй только "gemini-pro" (production для всех ADK/Capstone курсов)
        self.model_name = model
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    async def call(self, prompt, tools=None, system_instruction=None, max_retries=3):
        """
        Make async call to Gemini API with optional function calling.
        If system_instruction is given, prepend it to the prompt.
        """
        # Prepend system_instruction to prompt if it was provided
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
                return response.text if response else None
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise e
        return None
