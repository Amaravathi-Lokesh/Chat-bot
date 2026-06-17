import re


def is_heading(line):

    line = line.strip()

    if not line:
        return False

    if len(line) < 60:
        return True

    if line.isupper():
        return True

    if re.match(r"^\d+(\.\d+)*", line):
        return True

    return False


def chunk_text(text):

    text = text.replace("\r", "")

    lines = text.split("\n")

    sections = []

    current_section = ""

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if is_heading(line):

            if current_section:

                sections.append(
                    current_section.strip()
                )

            current_section = line + "\n"

        else:

            current_section += line + "\n"

    if current_section:

        sections.append(
            current_section.strip()
        )

    final_chunks = []

    MAX_SIZE = 1200

    OVERLAP = 200

    for section in sections:

        if len(section) <= MAX_SIZE:

            final_chunks.append(section)

        else:

            start = 0

            while start < len(section):

                end = start + MAX_SIZE

                piece = section[start:end]

                final_chunks.append(piece)

                start += MAX_SIZE - OVERLAP

    return final_chunks