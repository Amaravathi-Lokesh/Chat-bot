async def select_documents(ai,question,docs):

    if len(docs) <= 1:
        return docs

    document_list = ""

    for d in docs:

        document_list += f"""
ID:{d.id}

Name:{d.filename}

"""

    prompt = f"""
User question:

{question}

Available documents:

{document_list}

Return only document IDs separated by commas.

Example:

1,3

If none match return:

NONE
"""

    result = await ai.generate_response(
        prompt
    )

    result = result.strip()

    if result == "NONE":
        return docs

    try:

        ids = []

        for x in result.split(","):

            ids.append(
                int(x.strip())
            )

        selected = []

        for d in docs:

            if d.id in ids:

                selected.append(d)

        if len(selected):

            return selected

    except:
        pass

    return docs