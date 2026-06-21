from google import genai
from config.settings import settings
import traceback
from openai import OpenAI
class Ai:

    def __init__(self):

       self.client=OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.api_key
            )

    async def generate_response(self, prompt: str):

        try:
            #print("API KEY:", settings.api_key)
            response = self.client.chat.completions.create(
                model="poolside/laguna-xs.2:free",
                messages=[
                {
                    "role": "user",
                    "content": prompt
                }
                ],
                extra_body={"reasoning": {"enabled": True}}
                )

# Extract the assistant message with reasoning_details
            # response = 
            return response.choices[0].message.content
        except Exception as e:
            print("AI ERROR:", e)
            return "AI service is temporarily unavailable."
    async def stream_message(self, prompt: str):

        try:

            response = self.client.models.generate_content_stream(

                model="gemini-2.5-flash",

                contents=prompt

            )

            for chunk in response:

                if chunk.text:
                    yield chunk.text

        except Exception as e:
            print("AI ERROR:", repr(e))
            traceback.print_exc()
            yield "AI service is temporarily unavailable."