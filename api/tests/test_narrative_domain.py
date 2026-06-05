"""Tests for Scene and Narrative domain objects.

A Scene is the smallest addressable unit of a narrative: one coherent passage
of text with a title and a position within its parent Narrative.

A Narrative is the container: it holds an ordered list of Scenes and knows
its own title. Neither object touches the database – persistence is the
repository's job.
"""

import pytest

from api.exceptions.narrative import (
    ActorValidationError,
    NarrativeValidationError,
    SceneValidationError,
)
from api.models.narrative import Actor, ActorType, Narrative, Scene


# helper — actor with a fake id, as if already persisted
def _persisted_actor(label: str = "Max", actor_type: ActorType = ActorType.INDIVIDUAL) -> Actor:
    return Actor(id="actor-persisted", label=label, actor_type=actor_type, notes=None)


# --- Scene ---


def test_scene_create_stores_title_and_text() -> None:
    """Expects title, text, and position to be accessible after creation."""
    scene = Scene.create(title="Scene 1", text="A short text.", position=1)

    assert scene.title == "Scene 1"
    assert scene.text == "A short text."
    assert scene.position == 1


def test_scene_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    scene = Scene.create(title="Scene 1", text="A short text.", position=1)

    assert scene.id is None


def test_scene_create_raises_for_empty_text() -> None:
    """Expects a SceneValidationError because a Scene without text has no content."""
    with pytest.raises(SceneValidationError):
        Scene.create(title="Scene 1", text="", position=1)


def test_scene_create_raises_for_whitespace_only_text() -> None:
    """Expects a SceneValidationError because whitespace-only text is equivalent to empty."""
    with pytest.raises(SceneValidationError):
        Scene.create(title="Scene 1", text="   ", position=1)


def test_scene_create_raises_for_empty_title() -> None:
    """Expects a SceneValidationError because a Scene without a title cannot be addressed."""
    with pytest.raises(SceneValidationError):
        Scene.create(title="", text="A short text.", position=1)


def test_scene_create_raises_for_whitespace_only_title() -> None:
    """Expects a SceneValidationError because a whitespace-only title is equivalent to empty."""
    with pytest.raises(SceneValidationError):
        Scene.create(title="   ", text="A short text.", position=1)


def test_scene_from_record_reconstructs_scene() -> None:
    """Expects all fields – including the persisted id – to be restored from the database record."""
    record = {"id": "abc-123", "title": "Scene 1", "text": "A short text.", "position": 1}

    scene = Scene.from_record(record)

    assert scene.id == "abc-123"
    assert scene.title == "Scene 1"
    assert scene.text == "A short text."
    assert scene.position == 1


# --- Narrative ---


def test_narrative_create_raises_for_empty_title() -> None:
    """Expects NarrativeValidationError because a Narrative without a title cannot be identified."""
    with pytest.raises(NarrativeValidationError):
        Narrative.create(title="")


def test_narrative_create_raises_for_whitespace_only_title() -> None:
    """Expects a NarrativeValidationError because a whitespace-only title is equivalent to empty."""
    with pytest.raises(NarrativeValidationError):
        Narrative.create(title="   ")


def test_narrative_create_starts_with_no_scenes() -> None:
    """Expects a new Narrative to be an empty container – scenes are added explicitly."""
    narrative = Narrative.create(title="A Novel")

    assert narrative.scenes == []
    assert narrative.title == "A Novel"


def test_narrative_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    narrative = Narrative.create(title="A Novel")

    assert narrative.id is None


def test_narrative_add_scene_appends_scene() -> None:
    """Expects add_scene() to make the scene accessible via the scenes property."""
    narrative = Narrative.create(title="A Novel")
    scene = Scene.create(title="Szene 1", text="Es war einmal.", position=1)

    narrative.add_scene(scene)

    assert len(narrative.scenes) == 1
    assert narrative.scenes[0].title == "Szene 1"


def test_narrative_add_scene_preserves_order() -> None:
    """Expects scenes to appear in the order they were added – position is meaningful."""
    narrative = Narrative.create(title="A Novel")
    narrative.add_scene(Scene.create(title="Scene 1", text="First text.", position=1))
    narrative.add_scene(Scene.create(title="Scene 2", text="Second text.", position=2))

    assert narrative.scenes[0].position == 1
    assert narrative.scenes[1].position == 2


def test_narrative_from_record_reconstructs_narrative() -> None:
    """Expects id and title to be restored from the database record."""
    record = {"id": "xyz-456", "title": "A Novel"}

    narrative = Narrative.from_record(record)

    assert narrative.id == "xyz-456"
    assert narrative.title == "A Novel"


# --- Actor ---


def test_actor_create_stores_label_and_actor_type() -> None:
    """Expects label and actor_type to be accessible after creation."""
    actor = Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)

    assert actor.label == "Max"
    assert actor.actor_type == ActorType.INDIVIDUAL


def test_actor_create_stores_notes_when_provided() -> None:
    """Expects notes to be stored when explicitly passed."""
    actor = Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL, notes="The protagonist.")

    assert actor.notes == "The protagonist."


def test_actor_create_has_no_notes_by_default() -> None:
    """Expects notes to be None when not provided."""
    actor = Actor.create(label="Voters", actor_type=ActorType.GROUP)

    assert actor.notes is None


def test_actor_create_has_no_entity_ref_by_default() -> None:
    """Expects entity_ref to be None — not every actor maps to a causal model entity."""
    actor = Actor.create(label="Maria", actor_type=ActorType.INDIVIDUAL)

    assert actor.entity_ref is None


def test_actor_create_stores_entity_ref_when_provided() -> None:
    """Expects entity_ref to be stored when an ID of a causal model entity is given."""
    actor = Actor.create(
        label="Zentralbank",
        actor_type=ActorType.INSTITUTION,
        entity_ref="entity-uuid-123",
    )

    assert actor.entity_ref == "entity-uuid-123"


def test_actor_create_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    actor = Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)

    assert actor.id is None


def test_actor_create_raises_for_empty_label() -> None:
    """Expects ActorValidationError because an actor without a label cannot be addressed."""
    with pytest.raises(ActorValidationError):
        Actor.create(label="", actor_type=ActorType.INDIVIDUAL)


def test_actor_create_raises_for_whitespace_only_label() -> None:
    """Expects ActorValidationError because a whitespace-only label is equivalent to empty."""
    with pytest.raises(ActorValidationError):
        Actor.create(label="   ", actor_type=ActorType.INDIVIDUAL)


def test_actor_type_covers_all_expected_variants() -> None:
    """Expects all five actor types to exist in the enum."""
    types = {t.value for t in ActorType}

    assert "individual" in types
    assert "organisation" in types
    assert "group" in types
    assert "institution" in types
    assert "abstract_entity" in types


def test_actor_from_record_reconstructs_actor_with_notes() -> None:
    """Expects all fields including id and notes to be restored from the database record."""
    record = {
        "id": "actor-001",
        "label": "Max",
        "actor_type": "individual",
        "notes": "The protagonist.",
        "entity_ref": None,
    }

    actor = Actor.from_record(record)

    assert actor.id == "actor-001"
    assert actor.label == "Max"
    assert actor.actor_type == ActorType.INDIVIDUAL
    assert actor.notes == "The protagonist."
    assert actor.entity_ref is None


def test_actor_from_record_reconstructs_actor_with_entity_ref() -> None:
    """Expects entity_ref to be restored when the DB record contains one."""
    record = {
        "id": "actor-002",
        "label": "Zentralbank",
        "actor_type": "institution",
        "notes": None,
        "entity_ref": "entity-uuid-456",
    }

    actor = Actor.from_record(record)

    assert actor.entity_ref == "entity-uuid-456"


def test_actor_from_record_raises_for_unknown_type() -> None:
    """Expects ActorValidationError when the database record contains an unrecognised type value."""
    record = {
        "id": "actor-003",
        "label": "Max",
        "actor_type": "unknown_type",
        "notes": None,
        "entity_ref": None,
    }

    with pytest.raises(ActorValidationError):
        Actor.from_record(record)


def test_actor_update_changes_label_actor_type_and_notes() -> None:
    """Expects update() to change all mutable fields at once."""
    actor = _persisted_actor()

    actor.update(label="Maria", actor_type=ActorType.INDIVIDUAL, notes="Updated note.")

    assert actor.label == "Maria"
    assert actor.actor_type == ActorType.INDIVIDUAL
    assert actor.notes == "Updated note."


def test_actor_update_raises_for_empty_label() -> None:
    """Expects ActorValidationError when update() receives an empty label."""
    actor = _persisted_actor()

    with pytest.raises(ActorValidationError):
        actor.update(label="", actor_type=ActorType.INDIVIDUAL, notes=None)


def test_actor_update_raises_for_whitespace_only_label() -> None:
    """Expects ActorValidationError because a whitespace-only label is equivalent to empty."""
    actor = _persisted_actor()

    with pytest.raises(ActorValidationError):
        actor.update(label="   ", actor_type=ActorType.INDIVIDUAL, notes=None)


def test_actor_update_can_clear_notes() -> None:
    """Expects notes to become None when explicitly passed as None in update()."""
    actor = Actor(id="a1", label="Max", actor_type=ActorType.INDIVIDUAL, notes="Old note.")

    actor.update(label="Max", actor_type=ActorType.INDIVIDUAL, notes=None)

    assert actor.notes is None


# --- Narrative + Actor ---


def test_narrative_create_starts_with_no_actors() -> None:
    """Expects a new Narrative to have an empty actor list."""
    narrative = Narrative.create(title="A Novel")

    assert narrative.actors == []


def test_narrative_add_actor_appends_actor() -> None:
    """Expects add_actor() to make the actor accessible via the actors property."""
    narrative = Narrative.create(title="A Novel")
    actor = Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL)

    narrative.add_actor(actor)

    assert len(narrative.actors) == 1
    assert narrative.actors[0].label == "Max"


def test_narrative_add_actor_preserves_insertion_order() -> None:
    """Expects actors to appear in the order they were added."""
    narrative = Narrative.create(title="A Novel")
    narrative.add_actor(Actor.create(label="Max", actor_type=ActorType.INDIVIDUAL))
    narrative.add_actor(Actor.create(label="CDU", actor_type=ActorType.ORGANISATION))
    narrative.add_actor(Actor.create(label="Voters", actor_type=ActorType.GROUP))

    assert narrative.actors[0].label == "Max"
    assert narrative.actors[1].label == "CDU"
    assert narrative.actors[2].label == "Voters"


# --- Narrative + CausalModel link ---


def test_narrative_causal_model_id_is_none_by_default() -> None:
    """Expects a new Narrative to have no causal model linked."""
    narrative = Narrative.create(title="A Novel")

    assert narrative.causal_model_id is None


def test_narrative_link_to_causal_model_stores_id() -> None:
    """Expects link_to_causal_model() to make the id accessible via the property."""
    narrative = Narrative.create(title="A Novel")

    narrative.link_to_causal_model("model-xyz")

    assert narrative.causal_model_id == "model-xyz"


def test_narrative_link_to_causal_model_raises_for_empty_id() -> None:
    """Expects NarrativeValidationError when an empty string is passed as the model ID."""
    narrative = Narrative.create(title="A Novel")

    with pytest.raises(NarrativeValidationError):
        narrative.link_to_causal_model("")


def test_narrative_link_to_causal_model_raises_for_whitespace_only_id() -> None:
    """Expects NarrativeValidationError when a whitespace-only string is passed as the model ID."""
    narrative = Narrative.create(title="A Novel")

    with pytest.raises(NarrativeValidationError):
        narrative.link_to_causal_model("   ")


def test_narrative_from_record_reconstructs_causal_model_id() -> None:
    """Expects causal_model_id to be restored from the database record when present."""
    record = {"id": "xyz-456", "title": "A Novel", "causal_model_id": "model-xyz"}

    narrative = Narrative.from_record(record)

    assert narrative.causal_model_id == "model-xyz"


def test_narrative_from_record_accepts_missing_causal_model_id() -> None:
    """Expects causal_model_id to be None when the database record has no link."""
    record = {"id": "xyz-456", "title": "A Novel"}

    narrative = Narrative.from_record(record)

    assert narrative.causal_model_id is None


# --- Narrative.remove_actor ---


def test_narrative_remove_actor_removes_actor_by_id() -> None:
    """Expects the actor to be absent from the narrative after remove_actor is called."""
    narrative = Narrative.create(title="A Novel")
    actor = _persisted_actor()
    narrative.add_actor(actor)

    narrative.remove_actor("actor-persisted")

    assert len(narrative.actors) == 0


def test_narrative_remove_actor_is_noop_for_unknown_id() -> None:
    """Expects no error and no side effect when the id is not present."""
    narrative = Narrative.create(title="A Novel")
    actor = _persisted_actor()
    narrative.add_actor(actor)

    narrative.remove_actor("does-not-exist")

    assert len(narrative.actors) == 1


# --- Narrative + user_id ---


def test_narrative_has_no_user_id_by_default() -> None:
    """Expects a newly created Narrative to have user_id None before assignment."""
    narrative = Narrative.create("My Narrative")
    assert narrative.user_id is None


def test_assign_user_sets_user_id() -> None:
    """Expects assign_user() to set the user_id on the narrative."""
    narrative = Narrative.create("My Narrative")
    narrative.assign_user("00000000-0000-0000-0000-000000000001")
    assert narrative.user_id == "00000000-0000-0000-0000-000000000001"


def test_from_record_loads_user_id() -> None:
    """Expects from_record() to reconstruct a Narrative with its user_id."""
    record = {"id": "abc", "title": "Test", "user_id": "00000000-0000-0000-0000-000000000001"}
    narrative = Narrative.from_record(record)
    assert narrative.user_id == "00000000-0000-0000-0000-000000000001"
