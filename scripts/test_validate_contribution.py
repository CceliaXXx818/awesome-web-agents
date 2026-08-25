# ABOUTME: Tests for the contribution policy validator used by the lint workflow.
# ABOUTME: Run with `python3 -m unittest discover -s scripts -p "test_*.py"`.

from __future__ import annotations

import unittest

from validate_contribution import (
    REQUIRED_BODY_SECTIONS,
    extract_body_sections,
    new_items_in_diff,
    normalize_section,
)


BODY = """## Summary

Adds an item.

## Section

Dev Tools

## Why this belongs

It controls a browser.

## Primary documented web-agent use case

https://example.com/docs

## Public reference

https://example.com

## Affiliation disclosure

I maintain the project.

## Checklist

- [x] This PR adds exactly one item.
"""


class ExtractBodySectionsTest(unittest.TestCase):
    def test_reads_every_required_section(self) -> None:
        sections = extract_body_sections(BODY)
        for heading in REQUIRED_BODY_SECTIONS:
            self.assertTrue(sections.get(heading), f'missing "{heading}"')

    def test_reads_every_required_section_with_carriage_returns(self) -> None:
        # Some clients send the pull request body with CRLF line endings.
        sections = extract_body_sections(BODY.replace("\n", "\r\n"))
        for heading in REQUIRED_BODY_SECTIONS:
            self.assertTrue(sections.get(heading), f'missing "{heading}"')

    def test_section_name_has_no_carriage_return(self) -> None:
        sections = extract_body_sections(BODY.replace("\n", "\r\n"))
        self.assertEqual(normalize_section(sections["Section"]), "Dev Tools")

    def test_absent_section_is_not_reported(self) -> None:
        sections = extract_body_sections(BODY.replace("## Public reference", "## Other"))
        self.assertIsNone(sections.get("Public reference"))

    def test_empty_section_is_not_reported(self) -> None:
        sections = extract_body_sections(BODY.replace("https://example.com\n\n## Affiliation", "\n## Affiliation"))
        self.assertFalse(sections.get("Public reference"))


ITEM = "- [Zoom Search](https://github.com/goofrey/zoom-search) - A tool."
BADGED = ITEM + " ![stars](https://img.shields.io/github/stars/goofrey/zoom-search?style=social)"


class NewItemsInDiffTest(unittest.TestCase):
    def test_added_line_is_a_new_item(self) -> None:
        diff = "--- a/README.md\n+++ b/README.md\n@@ -1 +1,2 @@\n+" + ITEM
        self.assertEqual(new_items_in_diff(diff), [ITEM])

    def test_edited_line_is_not_a_new_item(self) -> None:
        # Changing the text of an entry that is already listed is maintenance.
        diff = "--- a/README.md\n+++ b/README.md\n@@ -1 +1 @@\n-" + ITEM + "\n+" + BADGED
        self.assertEqual(new_items_in_diff(diff), [])

    def test_an_edit_does_not_hide_a_new_item(self) -> None:
        other = "- [Other](https://example.com) - Another tool."
        diff = ("--- a/README.md\n+++ b/README.md\n@@ -1 +1,2 @@\n"
                "-" + ITEM + "\n+" + BADGED + "\n+" + other)
        self.assertEqual(new_items_in_diff(diff), [other])

    def test_removal_alone_adds_nothing(self) -> None:
        diff = "--- a/README.md\n+++ b/README.md\n@@ -1 +0,0 @@\n-" + ITEM
        self.assertEqual(new_items_in_diff(diff), [])

    def test_diff_headers_are_ignored(self) -> None:
        self.assertEqual(new_items_in_diff("--- a/README.md\n+++ b/README.md\n"), [])


if __name__ == "__main__":
    unittest.main()
