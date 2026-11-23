"""Splits an article's plain text into sections, one per main heading."""

import re

# Main sections that hold no useful knowledge, so we throw them away
UNWANTED_HEADINGS = ["references", "external links", "see also", "notes", "further reading"]

# Matches markers such as [12] or [citation needed]
MARKER_PATTERN = re.compile(r"\[(\d+|citation needed)\]")


def get_main_heading(line):
    """Return the title if the line is a main heading like == History ==.

    Returns None for any other line. Sub-headings like === Launch === are not
    main headings, so they stay inside the text of their section.
    """
    stripped = line.strip()
    is_main_heading = (
        stripped.startswith("==")
        and stripped.endswith("==")
        and not stripped.startswith("===")
    )
    if not is_main_heading:
        return None
    return stripped.strip("=").strip()


def clean_text(lines):
    """Join a list of lines into one clean string.

    Removes markers like [12], and turns a sub-heading such as === Launch ===
    into the plain line Launch.
    """
    cleaned_lines = []
    for line in lines:
        line = MARKER_PATTERN.sub("", line).strip()
        if line.startswith("=="):
            line = line.strip("=").strip()
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def keep_useful_sections(sections):
    """Drop unwanted and empty sections, and clean the text of the others."""
    useful_sections = []
    for section in sections:
        if section["heading"].lower() in UNWANTED_HEADINGS:
            continue

        text = clean_text(section["lines"])
        if text == "":
            continue
        useful_sections.append({"heading": section["heading"], "text": text})

    return useful_sections


def split_into_sections(article_text):
    """Split an article into a list of {"heading": ..., "text": ...} sections.

    The text before the first heading is the lead, and its heading is "Lead".
    """
    sections = []
    current_heading = "Lead"
    current_lines = []

    for line in article_text.split("\n"):
        new_heading = get_main_heading(line)

        if new_heading is None:
            current_lines.append(line)
            continue

        # A new main heading closes the section we were collecting
        sections.append({"heading": current_heading, "lines": current_lines})
        current_heading = new_heading
        current_lines = []

    # The last section has no heading after it, so we add it here
    sections.append({"heading": current_heading, "lines": current_lines})
    return keep_useful_sections(sections)