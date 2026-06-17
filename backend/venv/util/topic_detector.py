import re
from providers.ai import Ai
async def detect_topic(text):

    lines = text.split("\n")
    ai=Ai()
    for line in lines:

        line = line.strip()

        if len(line) < 5:
            continue

        if line.lower().startswith("assistant"):
            continue

        if line.lower().startswith("user"):
            continue

        if ":" not in line:

            prompt=f"""
        Find the main topic.

        Rules:
        - Maximum 4 words.
        - Return only topic.
        - No explanation.

        Text:

        {text[:1000]}

        Topic:
        """
            return await ai.generate_response(prompt)


    return "General"