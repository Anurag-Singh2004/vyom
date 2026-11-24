"""Cuts text into overlapping chunks of words."""


def chunk_text(text, chunk_size, overlap):
    """Cut one text into chunks of about chunk_size words.

    Each chunk starts overlap words before the end of the previous chunk, so a
    sentence that falls on a cut keeps some of its context.
    """
    # Without this check, the loop below would never move forward
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    # split() with no argument splits on any run of spaces and line breaks
    words = text.split()
    if len(words) == 0:
        return []

    # How many words we move forward for each new chunk
    step = chunk_size - overlap
    chunks = []
    start = 0

    while True:
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))

        # Once a chunk reaches the end of the text, we are finished
        if end >= len(words):
            break
        start = start + step

    return chunks


def chunk_article(record, chunk_size, overlap):
    """Cut every section of one article into chunks.

    Each chunk keeps the article title, URL and section heading, so we can
    show a citation later. The chunk id is the title plus a running number.
    """
    chunks = []
    chunk_number = 0

    for section in record["sections"]:
        for chunk_text_value in chunk_text(section["text"], chunk_size, overlap):
            chunks.append(
                {
                    "chunk_id": record["title"] + "#" + str(chunk_number),
                    "title": record["title"],
                    "url": record["url"],
                    "heading": section["heading"],
                    "text": chunk_text_value,
                }
            )
            chunk_number = chunk_number + 1

    return chunks