from google import genai
from config.settings import settings


class Ai:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.api_key
        )

    async def generate_response(self, prompt: str):

        try:

            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )

            return response.text
        except Exception as e:
           # print("AI ERROR:", e)
            return "AI service is temporarily unavailable."
    async def stream_message(self, prompt: str):

        try:

            response = self.client.models.generate_content_stream(

                model="gemini-2.5-flash-lite",

                contents=prompt

            )

            for chunk in response:

                if chunk.text:
                    yield chunk.text

        except Exception:

            yield "AI service is temporarily unavailable."