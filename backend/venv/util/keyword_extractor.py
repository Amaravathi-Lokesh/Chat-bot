import re

STOPWORDS = {

"a","an","the","is","are",

"of","to","and","in",

"for","with","on","by"

}

def extract_keywords(text):

    words = re.findall(

        r"\b[a-zA-Z]{4,}\b",

        text.lower()

    )

    unique = []

    seen = set()

    for w in words:

        if w in STOPWORDS:
            continue

        if w not in seen:

            seen.add(w)

            unique.append(w)

    return unique[:10]