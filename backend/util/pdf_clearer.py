import re

def clean_text(text: str):

    # Remove page numbers

    text = re.sub(

        r'Page\s+\d+',

        '',

        text,

        flags=re.IGNORECASE

    )

    # Remove multiple blank lines

    text = re.sub(

        r'\n+',

        '\n',

        text

    )

    # Remove multiple spaces

    text = re.sub(

        r'\s+',

        ' ',

        text

    )

    # Remove leading/trailing spaces

    text = text.strip()

    return text