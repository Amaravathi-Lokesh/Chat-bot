import re

def parse_document(text):

    text = text.replace("\r","")

    text = re.sub(
        r"User:",
        "\n\nUser:\n",
        text
    )

    text = re.sub(
        r"Assistant:",
        "\n\nAssistant:\n",
        text
    )

    blocks = text.split("\n\n")

    cleaned = []

    for block in blocks:

        block = block.strip()

        if len(block)<30:
            continue

        cleaned.append(block)

    return cleaned 