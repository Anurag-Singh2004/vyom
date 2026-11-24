"""Settings shared by all Vyom code: folder paths and chunk sizes."""

from pathlib import Path

# This file is src/vyom/config.py, so the project folder is three levels up
PROJECT_FOLDER = Path(__file__).resolve().parent.parent.parent

# Where the downloaded articles are, and where the chunks will be saved
RAW_FOLDER = PROJECT_FOLDER / "data" / "raw"
CHUNKS_FILE = PROJECT_FOLDER / "data" / "chunks.jsonl"

# Each chunk has about this many words
CHUNK_SIZE_WORDS = 200

# Each chunk repeats this many words from the end of the previous chunk
CHUNK_OVERLAP_WORDS = 40