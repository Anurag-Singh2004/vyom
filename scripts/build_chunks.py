"""Reads the downloaded articles, cuts them into chunks and saves them.

Run from the project folder with: PYTHONPATH=src python scripts/build_chunks.py
"""

import json

from vyom.chunker import chunk_article
from vyom.config import CHUNK_OVERLAP_WORDS, CHUNK_SIZE_WORDS, CHUNKS_FILE, RAW_FOLDER


def load_articles():
    """Read every article JSON file in data/raw/, except manifest.json."""
    articles = []

    # sorted() makes the file order, and so the chunk order, the same every run
    for file_path in sorted(RAW_FOLDER.glob("*.json")):
        if file_path.name == "manifest.json":
            continue
        with open(file_path, "r", encoding="utf-8") as article_file:
            articles.append(json.load(article_file))

    return articles


def save_chunks(chunks):
    """Write all chunks to data/chunks.jsonl, one JSON object per line."""
    lines = []
    for chunk in chunks:
        # ensure_ascii=False keeps letters such as accents readable
        lines.append(json.dumps(chunk, ensure_ascii=False))

    with open(CHUNKS_FILE, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(lines) + "\n")


def average_word_count(chunks):
    """Return the average number of words per chunk."""
    total_words = 0
    for chunk in chunks:
        total_words = total_words + len(chunk["text"].split())
    return total_words / len(chunks)


def main():
    """Chunk every article and save the result."""
    articles = load_articles()

    all_chunks = []
    for article in articles:
        article_chunks = chunk_article(article, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS)
        all_chunks.extend(article_chunks)

    save_chunks(all_chunks)

    print("Articles read:", len(articles))
    print("Chunks saved:", len(all_chunks))
    print("Average words per chunk:", round(average_word_count(all_chunks), 1))
    print("Saved to:", CHUNKS_FILE)


if __name__ == "__main__":
    main()