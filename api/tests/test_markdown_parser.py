"""Tests for MarkdownNarrativeParser.

The parser receives raw Markdown text and returns a list of Scene objects.
It knows nothing about files, databases, or services – pure transformation.

Our Markdown convention: scenes are delimited by horizontal rules (---) and
introduced by a level-3 heading (### Szene N). Everything before the first
scene heading (title, subtitle, preamble) is ignored by the parser.
"""

from api.parsers.markdown_narrative_parser import MarkdownNarrativeParser

SINGLE_SCENE_MARKDOWN = """\
# Klartext
## Eine Geschichte über eine Geschichte

---

### Szene 1

Es war ein Dienstag im Februar.
Die Küche war still.
"""

TWO_SCENE_MARKDOWN = """\
# Klartext
## Eine Geschichte über eine Geschichte

---

### Szene 1

Erster Text.

---

### Szene 2

Zweiter Text.
"""


# --- Happy path ---


def test_markdown_parser_returns_empty_list_for_empty_content() -> None:
    """Expects an empty list when the input is an empty string – not an error."""
    parser = MarkdownNarrativeParser()

    scenes = parser.parse("")

    assert scenes == []


def test_markdown_parser_creates_one_scene_from_single_scene_markdown() -> None:
    """Expects exactly one Scene when the input contains one ### heading."""
    parser = MarkdownNarrativeParser()

    scenes = parser.parse(SINGLE_SCENE_MARKDOWN)

    assert len(scenes) == 1


def test_markdown_parser_creates_two_scenes_from_two_scene_markdown() -> None:
    """Expects one Scene per ### heading found in the input."""
    parser = MarkdownNarrativeParser()

    scenes = parser.parse(TWO_SCENE_MARKDOWN)

    assert len(scenes) == 2


def test_markdown_parser_assigns_correct_title() -> None:
    """Expects the scene title to match the ### heading text, without the hashes."""
    parser = MarkdownNarrativeParser()

    scenes = parser.parse(SINGLE_SCENE_MARKDOWN)

    assert scenes[0].title == "Szene 1"


def test_markdown_parser_preserves_scene_text() -> None:
    """Expects all text between two headings to be kept as the scene's content."""
    parser = MarkdownNarrativeParser()

    scenes = parser.parse(SINGLE_SCENE_MARKDOWN)

    assert "Es war ein Dienstag im Februar." in scenes[0].text


def test_markdown_parser_assigns_positions_starting_at_one() -> None:
    """Expects positions to reflect reading order: first scene is 1, second is 2."""
    parser = MarkdownNarrativeParser()

    scenes = parser.parse(TWO_SCENE_MARKDOWN)

    assert scenes[0].position == 1
    assert scenes[1].position == 2


def test_markdown_parser_strips_surrounding_whitespace_from_text() -> None:
    """Expects leading and trailing whitespace to be removed – it is a Markdown artefact."""
    parser = MarkdownNarrativeParser()

    scenes = parser.parse(SINGLE_SCENE_MARKDOWN)

    assert scenes[0].text == scenes[0].text.strip()


# --- Error cases ---


def test_markdown_parser_returns_empty_list_for_content_without_scene_headings() -> None:
    """Expects an empty list when the content has no ### headings – no scenes to extract."""
    parser = MarkdownNarrativeParser()
    content = "Das ist irgendein Text ohne Szenen-Struktur.\nNoch eine Zeile."

    scenes = parser.parse(content)

    assert scenes == []


def test_markdown_parser_returns_empty_list_for_random_symbols() -> None:
    """Expects an empty list for arbitrary symbol noise – the parser must not crash."""
    parser = MarkdownNarrativeParser()
    content = "!@#$%^&*()_+{}|:<>?[];',./`~"

    scenes = parser.parse(content)

    assert scenes == []


def test_markdown_parser_skips_scene_with_empty_body() -> None:
    """Expects a scene with a heading but no text to be skipped – empty scenes are invalid."""
    parser = MarkdownNarrativeParser()
    content = """\
# Titel

---

### Szene 1

---

### Szene 2

Zweiter Text.
"""

    scenes = parser.parse(content)

    assert len(scenes) == 1
    assert scenes[0].title == "Szene 2"
