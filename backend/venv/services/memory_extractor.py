import json
class MemoryExtractor:

    def __init__(self, ai):

        self.ai = ai

    async def extract(

        self,

        message

    ):

        prompt=f"""

Extract permanent user facts.

Message:

{message}

Extract only:

name

college

city

skills

project

Return JSON.

Example:

{{
"name":"Lokesh",
"college":"SVCE"
}}

If nothing important exists:

{{}}

Only JSON.

"""

        response=await self.ai.generate_response(
            prompt
        )

        try:

            response=response.replace(
                "```json",
                ""
            )

            response=response.replace(
                "```",
                ""
            )

            return json.loads(
                response
            )

        except:

            return {}