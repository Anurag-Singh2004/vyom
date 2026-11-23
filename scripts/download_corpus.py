"""Downloads the Wikipedia articles for Vyom and saves them in data/raw/."""

import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

from text_cleaning import split_into_sections
from wiki_client import create_session, get_article, get_links

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
SEED_FILE = PROJECT_FOLDER / "scripts" / "seed_titles.txt"
RAW_FOLDER = PROJECT_FOLDER / "data" / "raw"

# Total number of articles we want, seed articles included
MAXIMUM_ARTICLES = 100

# An extra article is kept only if at least this many seed articles link to it
MINIMUM_SEED_LINKS = 2

# General pages that many seeds link to, but that are too broad to be useful
UNWANTED_TITLES = ["India", "Launch vehicle"]


def read_seed_titles():
    """Read the seed titles from seed_titles.txt, skipping comments and blank lines."""
    titles = []
    with open(SEED_FILE, "r", encoding="utf-8") as seed_file:
        for line in seed_file:
            line = line.strip()
            if line != "" and not line.startswith("#"):
                titles.append(line)
    return titles


def download_article(session, requested_title):
    """Download one article and return it as a dictionary, or None if missing."""
    article = get_article(session, requested_title)
    if article is None:
        return None

    return {
        "title": article["title"],
        "url": article["url"],
        "retrieved_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "revision_id": article["revision_id"],
        "sections": split_into_sections(article["text"]),
        "outgoing_links": get_links(session, article["title"]),
    }


def save_article(record):
    """Save one article as its own JSON file in data/raw/."""
    RAW_FOLDER.mkdir(parents=True, exist_ok=True)

    # quote() writes unusual characters as %XX, so every title gets its own file name
    file_name = quote(record["title"].replace(" ", "_"), safe="") + ".json"

    with open(RAW_FOLDER / file_name, "w", encoding="utf-8") as output_file:
        json.dump(record, output_file, ensure_ascii=False, indent=2)


def download_and_save(session, requested_title, saved_titles):
    """Download one title and save it, unless it is missing or already saved.

    Returns the record, or None when nothing new was saved.
    """
    record = download_article(session, requested_title)

    if record is None:
        print("  MISSING: no article with this title")
        return None
    if record["title"] in saved_titles:
        print("  skipped: same article as one already saved")
        return None

    save_article(record)
    saved_titles.add(record["title"])
    return record


def choose_extra_titles(links_by_seed):
    """Choose extra articles to download, based on the links of the seed articles.

    Keeps a title only if at least MINIMUM_SEED_LINKS different seeds link to it.
    Seeds, years, list pages and very general pages are skipped.
    """
    # Count how many different seeds link to each title
    link_counts = {}
    for link_titles in links_by_seed.values():
        for title in set(link_titles):
            link_counts[title] = link_counts.get(title, 0) + 1

    candidates = []
    for title, count in link_counts.items():
        if count < MINIMUM_SEED_LINKS or title in links_by_seed:
            continue
        # Skip years, list pages (mostly tables) and very general pages
        if title[0].isdigit() or title.startswith("List of") or title in UNWANTED_TITLES:
            continue
        # The count is negative so that sorting puts the most linked titles first
        candidates.append((-count, title))
    candidates.sort()

    free_slots = MAXIMUM_ARTICLES - len(links_by_seed)
    return [title for count, title in candidates[:free_slots]]

def write_manifest(saved_titles):
    """Write data/raw/manifest.json, which describes this download."""
    manifest = {
        "source": "English Wikipedia",
        "license": "CC BY-SA 4.0",
        "retrieval_date": datetime.now(UTC).date().isoformat(),
        "article_count": len(saved_titles),
        "titles": sorted(saved_titles),
    }
    with open(RAW_FOLDER / "manifest.json", "w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file, ensure_ascii=False, indent=2)


def main():
    """Download the seeds, choose extra articles from their links, download those."""
    session = create_session()
    seed_titles = read_seed_titles()
    saved_titles = set()
    links_by_seed = {}

    for position, title in enumerate(seed_titles, start=1):
        print("[seed " + str(position) + "/" + str(len(seed_titles)) + "]", title)
        record = download_and_save(session, title, saved_titles)
        if record is not None:
            links_by_seed[record["title"]] = record["outgoing_links"]

    extra_titles = choose_extra_titles(links_by_seed)
    print("Seeds saved:", len(links_by_seed), "| extra articles chosen:", len(extra_titles))

    for position, title in enumerate(extra_titles, start=1):
        print("[extra " + str(position) + "/" + str(len(extra_titles)) + "]", title)
        download_and_save(session, title, saved_titles)

    write_manifest(saved_titles)
    print("Done. Articles saved:", len(saved_titles))


if __name__ == "__main__":
    main()