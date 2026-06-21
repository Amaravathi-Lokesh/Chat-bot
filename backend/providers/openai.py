from openai import OpenAI
from config.settings import settings
class AIservice:
    def __init__(self):
        self.client=OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openapi_key
            )
    async def generate_response(self,prompt):

            try:

                response=self.client.chat.completions.create(

                    model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",

                    messages=[

                        {

                            "role":"user",

                            "content":prompt

                        }

                    ],

                    extra_body={

                        "reasoning":{

                            "enabled":True

                        }

                    }

                )

                return response.choices[0].message.content

            except Exception as e:

                print(e)

                return "OPENAI service is temporarily unavailable."