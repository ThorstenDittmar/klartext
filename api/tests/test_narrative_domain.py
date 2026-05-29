"""Tests for Scene and Narrative domain objects.

A Scene is the smallest addressable unit of a narrative: one coherent passage
of text with a title and a position within its parent Narrative.

A Narrative is the container: it holds an ordered list of Scenes and knows
its own title. Neither object touches the database – persistence is the
repository's job.
"""

import pytest

from api.exceptions.narrative import ActorValidationError, NarrativeValidationError, SceneValidationError
from api.models.narrative import Actor, ActorType, Narrative, Scene


# helper — actor with a fake id, as if already persisted
def _persisted_actor(name: str = "Max", typ: ActorType = ActorType.INDIVIDUAL) -> Actor:
    return Actor(id="actor-persisted", name=name, typ=typ, description=None)


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
    """Expects a NarrativeValidationError because a Narrative without a title cannot be identified."""
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


def test_actor_create_stores_name_and_type() -> None:
    """Expects name and type to be accessible after creation."""
    actor = Actor.create(name="Max", typ=ActorType.INDIVIDUAL)

    assert actor.name == "Max"
    assert actor.typ == ActorType.INDIVIDUAL


def test_actor_create_stores_description_when_provided() -> None:
    """Expects description to be stored when explicitly passed."""
    actor = Actor.create(name="Max", typ=ActorType.INDIVIDUAL, description="The protagonist.")

    assert actor.description == "The protagonist."


def test_actor_create_has_no_description_by_default() -> None:
    """Expects description to be None when not provided."""
    actor = Actor.create(name="Voters", typ=ActorType.GROUP)

    assert actor.description is None


def test_actor_create_has_no_id_before_persistence() -> None:
    """Expects id to be None until the repository assigns one on first save."""
    actor = Actor.create(name="Max", typ=ActorType.INDIVIDUAL)

    assert actor.id is None


def test_actor_create_raises_for_empty_name() -> None:
    """Expects ActorValidationError because an actor without a name cannot be addressed."""
    with pytest.raises(ActorValidationError):
        Actor.create(name="", typ=ActorType.INDIVIDUAL)


def test_actor_create_raises_for_whitespace_only_name() -> None:
    """Expects ActorValidationError because a whitespace-only name is equivalent to empty."""
    with pytest.raises(ActorValidationError):
        Actor.create(name="   ", typ=ActorType.INDIVIDUAL)


def test_actor_type_covers_all_expected_variants() -> None:
    """Expects all five actor types to exist in the enum."""
    types = {t.value for t in ActorType}

    assert "individual" in types
    assert "organisation" in types
    assert "group" in types
    assert "institution" in types
    assert "abstract_entity" in types


def test_actor_from_record_reconstructs_actor_with_description() -> None:
    """Expects all fields including id and description to be restored from the database record."""
    record = {
        "id": "actor-001",
        "name": "Max",
        "typ": "individual",
        "description": "The protagonist.",
    }

    actor = Actor.from_record(record)

    assert actor.id == "actor-001"
    assert actor.name == "Max"
    assert actor.typ == ActorType.INDIVIDUAL
    assert actor.description == "The protagonist."


def test_actor_from_record_reconstructs_actor_without_description() -> None:
    """Expects description to be None when the database record has no description."""
    record = {"id": "actor-002", "name": "Voters", "typ": "group", "description": None}

    actor = Actor.from_record(record)

    assert actor.description is None


def test_actor_from_record_raises_for_unknown_type() -> None:
    """Expects ActorValidationError when the database record contains an unrecognised type value."""
    record = {"id": "actor-003", "name": "Max", "typ": "unknown_type", "description": None}

    with pytest.raises(ActorValidationError):
        Actor.from_record(record)


# --- Narrative + Actor ---


def test_narrative_create_starts_with_no_actors() -> None:
    """Expects a new Narrative to have an empty actor list."""
    narrative = Narrative.create(title="A Novel")

    assert narrative.actors == []


def test_narrative_add_actor_appends_actor() -> None:
    """Expects add_actor() to make the actor accessible via the actors property."""
    narrative = Narrative.create(title="A Novel")
    actor = Actor.create(name="Max", typ=ActorType.INDIVIDUAL)

    narrative.add_actor(actor)

    assert len(narrative.actors) == 1
    assert narrative.actors[0].name == "Max"


def test_narrative_add_actor_preserves_insertion_order() -> None:
    """Expects actors to appear in the order they were added."""
    narrative = Narrative.create(title="A Novel")
    narrative.add_actor(Actor.create(name="Max", typ=ActorType.INDIVIDUAL))
    narrative.add_actor(Actor.create(name="CDU", typ=ActorType.ORGANISATION))
    narrative.add_actor(Actor.create(name="Voters", typ=ActorType.GROUP))

    assert narrative.actors[0].name == "Max"
    assert narrative.actors[1].name == "CDU"
    assert narrative.actors[2].name == "Voters"


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


# --- Actor.update ---


def test_actor_update_changes_all_fields() -> None:
    """Expects name, type and description to reflect the new values after update."""
    actor = _persisted_actor()

    actor.update(name="CDU", typ=ActorType.ORGANISATION, description="A party.")

    assert actor.name == "CDU"
    assert actor.typ == ActorType.ORGANISATION
    assert actor.description == "A party."


def test_actor_update_can_clear_description() -> None:
    """Expects description to become None when explicitly passed as None."""
    actor = Actor(id="a1", name="Max", typ=ActorType.INDIVIDUAL, description="Old description.")

    actor.update(name="Max", typ=ActorType.INDIVIDUAL, description=None)

    assert actor.description is None


def test_actor_update_raises_for_empty_name() -> None:
    """Expects ActorValidationError because an empty name is invalid."""
    actor = _persisted_actor()

    with pytest.raises(ActorValidationError):
        actor.update(name="", typ=ActorType.INDIVIDUAL, description=None)


def test_actor_update_raises_for_whitespace_only_name() -> None:
    """Expects ActorValidationError because a whitespace-only name is equivalent to empty."""
    actor = _persisted_actor()

    with pytest.raises(ActorValidationError):
        actor.update(name="   ", typ=ActorType.INDIVIDUAL, description=None)


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
