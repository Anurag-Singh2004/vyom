"""Talks to the English Wikipedia API. Every network call lives in this file."""

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

API_URL = "https://en.wikipedia.org/w/api.php"

# Wait a little after each  request
DELAY_SECONDS = 0.5


def create_session():
    """Create an HTTP session that tells Wikipedia who we are.

    Wikipedia asks every program to send a User-Agent with a contact email.
    """
    # The .env file is in the project folder, one level above scripts/
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    email = os.getenv("WIKIPEDIA_CONTACT_EMAIL", "")

    if email == "" or email == "your-email@example.com":
        raise RuntimeError("Set WIKIPEDIA_CONTACT_EMAIL in the .env file first.")

    session = requests.Session()
    session.headers["User-Agent"] = "Vyom/0.1 (contact: " + email + ")"
    return session


def ask_wikipedia(session, parameters):
    """Send one query to the API and return the answer as a dictionary."""
    # Copy the settings so the caller's dictionary is not changed
    full_parameters = dict(parameters)
    full_parameters["action"] = "query"
    full_parameters["format"] = "json"
    full_parameters["formatversion"] = "2"

    response = session.get(API_URL, params=full_parameters, timeout=30)
    # Stops the program with an error if Wikipedia answered with a failure code
    response.raise_for_status()
    time.sleep(DELAY_SECONDS)
    return response.json()


def get_article(session, title):
    """Get the plain text, URL and revision id of one article.

    Follows redirects. Returns None if the article does not exist.
    """
    parameters = {
        "titles": title,
        "prop": "extracts|info",
        "inprop": "url",
        # Plain text instead of HTML
        "explaintext": "1",
        # Section headings are written like == Heading ==
        "exsectionformat": "wiki",
        "redirects": "1",
    }
    answer = ask_wikipedia(session, parameters)
    page = answer["query"]["pages"][0]

    if page.get("missing"):
        return None

    return {
        "title": page["title"],
        "url": page["fullurl"],
        "revision_id": page.get("lastrevid"),
        "text": page.get("extract", ""),
    }


def get_links(session, title):
    """Get the titles of all normal articles that this article links to."""
    link_titles = []
    parameters = {
        "titles": title,
        "prop": "links",
        # Namespace 0 means normal articles only (no Talk or Category pages)
        "plnamespace": "0",
        "pllimit": "max",
        "redirects": "1",
    }

    # A long article has more links than one answer can hold, so we repeat
    while True:
        answer = ask_wikipedia(session, parameters)
        page = answer["query"]["pages"][0]

        for link in page.get("links", []):
            link_titles.append(link["title"])

        # Wikipedia sends "continue" only when more links are waiting
        if "continue" not in answer:
            break
        parameters["plcontinue"] = answer["continue"]["plcontinue"]

    return link_titles