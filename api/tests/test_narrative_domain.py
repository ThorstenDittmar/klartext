"""Tests for Scene and Narrative domain objects.

A Scene is the smallest addressable unit of a narrative: one coherent passage
of text with a title and a position within its parent Narrative.

A Narrative is the container: it holds an ordered list of Scenes and knows
its own title. Neither object touches the database – persistence is the
repository's job.
"""

import pytest

from api.exceptions.narrative import NarrativeValidationError, SceneValidationError
from api.models.narrative import Narrative, Scene


# --- Scene ---


def test_scene_create_stores_title_and_text() -> None:
    """Expects title, text, and position to be accessible after creation."""
    scene = Scene.create(title="Szene 1", text="Es war einmal.", position=1)

    assert scene.title == "Szene 1"
    assert scene.text == "Es war einmal."
    assert scene.position == 1


def test_scene_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    scene = Scene.create(title="Szene 1", text="Es war einmal.", position=1)

    assert scene.id is None


def test_scene_create_raises_for_empty_text() -> None:
    """Expects a SceneValidationError because a Scene without text has no content."""
    with pytest.raises(SceneValidationError):
        Scene.create(title="Szene 1", text="", position=1)


def test_scene_create_raises_for_whitespace_only_text() -> None:
    """Expects a SceneValidationError because whitespace-only text is equivalent to empty."""
    with pytest.raises(SceneValidationError):
        Scene.create(title="Szene 1", text="   ", position=1)


def test_scene_create_raises_for_empty_title() -> None:
    """Expects a SceneValidationError because a Scene without a title cannot be addressed."""
    with pytest.raises(SceneValidationError):
        Scene.create(title="", text="Es war einmal.", position=1)


def test_scene_create_raises_for_whitespace_only_title() -> None:
    """Expects a SceneValidationError because a whitespace-only title is equivalent to empty."""
    with pytest.raises(SceneValidationError):
        Scene.create(title="   ", text="Es war einmal.", position=1)


def test_scene_from_record_reconstructs_scene() -> None:
    """Expects all fields – including the persisted id – to be restored from the database record."""
    record = {"id": "abc-123", "title": "Szene 1", "text": "Es war einmal.", "position": 1}

    scene = Scene.from_record(record)

    assert scene.id == "abc-123"
    assert scene.title == "Szene 1"
    assert scene.text == "Es war einmal."
    assert scene.position == 1


# --- Narrative ---


def test_narrative_create_raises_for_empty_title() -> None:
    """Expects a NarrativeValidationError because a Narrative without a title cannot be identified."""
    with pytest.raises(NarrativeValidationError):
        Narrative.create(title="")


def test_narrative_create_raises_for_whitespace_only_title() -> None:
    """Expects a NarrativeValidationError because a whitespace-only title is equivalent to empty."""
    with pytest.raises(NarrativeValidationError):
        Narrative.create(title="   ")


def test_narrative_create_starts_with_no_scenes() -> None:
    """Expects a new Narrative to be an empty container – scenes are added explicitly."""
    narrative = Narrative.create(title="Mein Roman")

    assert narrative.scenes == []
    assert narrative.title == "Mein Roman"


def test_narrative_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    narrative = Narrative.create(title="Mein Roman")

    assert narrative.id is None


def test_narrative_add_scene_appends_scene() -> None:
    """Expects add_scene() to make the scene accessible via the scenes property."""
    narrative = Narrative.create(title="Mein Roman")
    scene = Scene.create(title="Szene 1", text="Es war einmal.", position=1)

    narrative.add_scene(scene)

    assert len(narrative.scenes) == 1
    assert narrative.scenes[0].title == "Szene 1"


def test_narrative_add_scene_preserves_order() -> None:
    """Expects scenes to appear in the order they were added – position is meaningful."""
    narrative = Narrative.create(title="Mein Roman")
    narrative.add_scene(Scene.create(title="Szene 1", text="Erster Text.", position=1))
    narrative.add_scene(Scene.create(title="Szene 2", text="Zweiter Text.", position=2))

    assert narrative.scenes[0].position == 1
    assert narrative.scenes[1].position == 2


def test_narrative_from_record_reconstructs_narrative() -> None:
    """Expects id and title to be restored from the database record."""
    record = {"id": "xyz-456", "title": "Mein Roman"}

    narrative = Narrative.from_record(record)

    assert narrative.id == "xyz-456"
    assert narrative.title == "Mein Roman"
