"""Tests for NarrativeService.

NarrativeService orchestrates two collaborators:
  1. NarrativeImportService – reads a file from disk and parses it.
  2. NarrativeRepository – persists and retrieves Narratives.

Tests inject a FakeNarrativeParser (no Markdown parsing) and the shared
FakeNarrativeRepository (no database involved).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from api.exceptions.narrative import (
    ActorNotFoundError,
    NarrativeFileNotFoundError,
    NarrativeNotFoundError,
)
from api.models.narrative import ActorType, Scene
from api.parsers.narrative_parser import NarrativeParser
from api.repositories.narrative_repository import NarrativeRepository
from api.services.narrative_import_service import NarrativeImportService
from api.services.narrative_service import NarrativeService
from tests.fakes.fake_narrative_repository import FakeNarrativeRepository

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "klartext-eine-geschichte-ueber-eine-geschichte"
    / "narrative.md"
)

NONEXISTENT_PATH = Path("/tmp/does_not_exist/narrative.md")


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeNarrativeParser(NarrativeParser):
    """Returns two fixed scenes regardless of content."""

    def parse(self, content: str) -> list[Scene]:
        return [
            Scene.create(title="Scene 1", text="Fake text.", position=1),
            Scene.create(title="Scene 2", text="Also fake.", position=2),
        ]


def make_service(
    parser: NarrativeParser | None = None,
    repository: NarrativeRepository | None = None,
) -> NarrativeService:
    return NarrativeService(
        import_service=NarrativeImportService(parser=parser or FakeNarrativeParser()),
        repository=repository or FakeNarrativeRepository(),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_import_returns_narrative_with_id() -> None:
    """Expects import_from_file to return a Narrative with a non-None ID after saving."""
    service = make_service()

    narrative = await service.import_from_file(FIXTURE_PATH)

    assert narrative.id is not None


@pytest.mark.asyncio
async def test_narrative_service_import_returns_narrative_with_scenes() -> None:
    """Expects the returned Narrative to contain the scenes produced by the parser."""
    service = make_service()

    narrative = await service.import_from_file(FIXTURE_PATH)

    assert len(narrative.scenes) == 2


@pytest.mark.asyncio
async def test_narrative_service_import_assigns_ids_to_scenes() -> None:
    """Expects each scene in the saved Narrative to have a non-None ID."""
    service = make_service()

    narrative = await service.import_from_file(FIXTURE_PATH)

    assert all(scene.id is not None for scene in narrative.scenes)


@pytest.mark.asyncio
async def test_narrative_service_find_by_id_returns_saved_narrative() -> None:
    """Expects find_by_id to return the Narrative that was previously imported."""
    service = make_service()
    saved = await service.import_from_file(FIXTURE_PATH)

    found = await service.find_by_id(saved.id)  # type: ignore[arg-type]

    assert found.id == saved.id
    assert len(found.scenes) == 2


@pytest.mark.asyncio
async def test_narrative_service_list_all_includes_imported_narrative() -> None:
    """Expects list_all to contain the Narrative after it has been imported."""
    service = make_service()
    saved = await service.import_from_file(FIXTURE_PATH)

    all_narratives = await service.list_all()

    ids = [n.id for n in all_narratives]
    assert saved.id in ids


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_import_raises_for_nonexistent_file() -> None:
    """Expects NarrativeFileNotFoundError when the given path does not exist."""
    service = make_service()

    with pytest.raises(NarrativeFileNotFoundError):
        await service.import_from_file(NONEXISTENT_PATH)


@pytest.mark.asyncio
async def test_narrative_service_find_by_id_raises_for_unknown_id() -> None:
    """Expects NarrativeNotFoundError when no Narrative exists for the given ID."""
    service = make_service()

    with pytest.raises(NarrativeNotFoundError):
        await service.find_by_id("00000000-0000-0000-0000-000000000000")


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_create_returns_narrative_with_id() -> None:
    """Expects create to return a Narrative with a non-None ID after saving."""
    service = make_service()

    narrative = await service.create("My Narrative")

    assert narrative.id is not None


@pytest.mark.asyncio
async def test_narrative_service_create_returns_narrative_with_correct_title() -> None:
    """Expects the returned Narrative to carry the title that was passed in."""
    service = make_service()

    narrative = await service.create("My Narrative")

    assert narrative.title == "My Narrative"


@pytest.mark.asyncio
async def test_narrative_service_create_returns_empty_narrative() -> None:
    """Expects the new Narrative to have no scenes."""
    service = make_service()

    narrative = await service.create("My Narrative")

    assert narrative.scenes == []


@pytest.mark.asyncio
async def test_narrative_service_create_raises_for_empty_title() -> None:
    """Expects NarrativeValidationError when an empty title is provided."""
    from api.exceptions.narrative import NarrativeValidationError

    service = make_service()

    with pytest.raises(NarrativeValidationError):
        await service.create("")


@pytest.mark.asyncio
async def test_narrative_service_create_raises_for_whitespace_only_title() -> None:
    """Expects NarrativeValidationError when the title contains only whitespace."""
    from api.exceptions.narrative import NarrativeValidationError

    service = make_service()

    with pytest.raises(NarrativeValidationError):
        await service.create("   ")


# ---------------------------------------------------------------------------
# add_scene
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_add_scene_returns_scene_with_id() -> None:
    """Expects add_scene to return a Scene with a non-None ID."""
    service = make_service()
    narrative = await service.create("My Narrative")

    scene = await service.add_scene(narrative.id, "Scene 1", "A short text.")  # type: ignore[arg-type]

    assert scene.id is not None


@pytest.mark.asyncio
async def test_narrative_service_add_scene_returns_scene_with_correct_title_and_text() -> None:
    """Expects the returned Scene to carry the title and text that were passed in."""
    service = make_service()
    narrative = await service.create("My Narrative")

    scene = await service.add_scene(narrative.id, "Scene 1", "A short text.")  # type: ignore[arg-type]

    assert scene.title == "Scene 1"
    assert scene.text == "A short text."


@pytest.mark.asyncio
async def test_narrative_service_add_scene_assigns_sequential_positions() -> None:
    """Expects scenes added in sequence to receive positions 1, 2, 3."""
    service = make_service()
    narrative = await service.create("My Narrative")

    s1 = await service.add_scene(narrative.id, "Scene 1", "Text for scene 1.")  # type: ignore[arg-type]
    s2 = await service.add_scene(narrative.id, "Scene 2", "Text for scene 2.")  # type: ignore[arg-type]
    s3 = await service.add_scene(narrative.id, "Scene 3", "Text for scene 3.")  # type: ignore[arg-type]

    assert s1.position == 1
    assert s2.position == 2
    assert s3.position == 3


@pytest.mark.asyncio
async def test_narrative_service_add_scene_raises_for_unknown_narrative_id() -> None:
    """Expects NarrativeNotFoundError when the narrative does not exist."""
    service = make_service()

    with pytest.raises(NarrativeNotFoundError):
        await service.add_scene("00000000-0000-0000-0000-000000000000", "Szene", "Text.")


@pytest.mark.asyncio
async def test_narrative_service_add_scene_raises_for_empty_title() -> None:
    """Expects SceneValidationError when the scene title is empty."""
    from api.exceptions.narrative import SceneValidationError

    service = make_service()
    narrative = await service.create("My Narrative")

    with pytest.raises(SceneValidationError):
        await service.add_scene(narrative.id, "", "A text.")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_narrative_service_add_scene_raises_for_whitespace_only_title() -> None:
    """Expects SceneValidationError when the scene title contains only whitespace."""
    from api.exceptions.narrative import SceneValidationError

    service = make_service()
    narrative = await service.create("My Narrative")

    with pytest.raises(SceneValidationError):
        await service.add_scene(narrative.id, "   ", "A text.")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_narrative_service_add_scene_raises_for_empty_text() -> None:
    """Expects SceneValidationError when the scene text is empty."""
    from api.exceptions.narrative import SceneValidationError

    service = make_service()
    narrative = await service.create("My Narrative")

    with pytest.raises(SceneValidationError):
        await service.add_scene(narrative.id, "Scene 1", "")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_narrative_service_add_scene_raises_for_whitespace_only_text() -> None:
    """Expects SceneValidationError when the scene text contains only whitespace."""
    from api.exceptions.narrative import SceneValidationError

    service = make_service()
    narrative = await service.create("My Narrative")

    with pytest.raises(SceneValidationError):
        await service.add_scene(narrative.id, "Scene 1", "   ")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# add_actor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_add_actor_returns_actor_with_id() -> None:
    """Expects add_actor to return an Actor with a non-None ID after persisting."""
    service = make_service()
    narrative = await service.create("My Narrative")

    actor = await service.add_actor(narrative.id, "Max", ActorType.INDIVIDUAL)  # type: ignore[arg-type]

    assert actor.id is not None


@pytest.mark.asyncio
async def test_narrative_service_add_actor_returns_actor_with_correct_name_and_type() -> None:
    """Expects the returned Actor to carry the label and actor_type that were passed in."""
    service = make_service()
    narrative = await service.create("My Narrative")

    actor = await service.add_actor(narrative.id, "CDU", ActorType.ORGANISATION)  # type: ignore[arg-type]

    assert actor.label == "CDU"
    assert actor.actor_type == ActorType.ORGANISATION


@pytest.mark.asyncio
async def test_narrative_service_add_actor_notes_defaults_to_none() -> None:
    """Expects notes to be None when not provided."""
    service = make_service()
    narrative = await service.create("My Narrative")

    actor = await service.add_actor(narrative.id, "Voters", ActorType.GROUP)  # type: ignore[arg-type]

    assert actor.notes is None


@pytest.mark.asyncio
async def test_narrative_service_add_actor_raises_for_unknown_narrative_id() -> None:
    """Expects NarrativeNotFoundError when the narrative does not exist."""
    service = make_service()

    with pytest.raises(NarrativeNotFoundError):
        await service.add_actor("00000000-0000-0000-0000-000000000000", "Max", ActorType.INDIVIDUAL)


@pytest.mark.asyncio
async def test_narrative_service_add_actor_raises_for_empty_label() -> None:
    """Expects ActorValidationError when the actor label is empty."""
    from api.exceptions.narrative import ActorValidationError

    service = make_service()
    narrative = await service.create("My Narrative")

    with pytest.raises(ActorValidationError):
        await service.add_actor(narrative.id, "", ActorType.INDIVIDUAL)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# update_actor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_update_actor_returns_actor_with_updated_fields() -> None:
    """Expects update_actor to return an Actor carrying the new label, actor_type and notes."""
    service = make_service()
    narrative = await service.create("My Narrative")
    actor = await service.add_actor(narrative.id, "Max", ActorType.INDIVIDUAL)  # type: ignore[arg-type]

    assert narrative.id is not None
    assert actor.id is not None
    updated = await service.update_actor(
        narrative.id, actor.id, "CDU", ActorType.ORGANISATION, "A party."
    )

    assert updated.label == "CDU"
    assert updated.actor_type == ActorType.ORGANISATION
    assert updated.notes == "A party."


@pytest.mark.asyncio
async def test_narrative_service_update_actor_raises_for_unknown_narrative_id() -> None:
    """Expects NarrativeNotFoundError when the narrative does not exist."""
    service = make_service()

    with pytest.raises(NarrativeNotFoundError):
        await service.update_actor(
            "00000000-0000-0000-0000-000000000000",
            "actor-id",
            "Max",
            ActorType.INDIVIDUAL,
            None,
        )


@pytest.mark.asyncio
async def test_narrative_service_update_actor_raises_for_unknown_actor_id() -> None:
    """Expects ActorNotFoundError when the actor does not exist in the narrative."""
    service = make_service()
    narrative = await service.create("My Narrative")

    assert narrative.id is not None
    with pytest.raises(ActorNotFoundError):
        await service.update_actor(
            narrative.id, "00000000-0000-0000-0000-000000000000", "Max", ActorType.INDIVIDUAL, None
        )


@pytest.mark.asyncio
async def test_narrative_service_update_actor_raises_for_empty_label() -> None:
    """Expects ActorValidationError when the new label is empty."""
    from api.exceptions.narrative import ActorValidationError

    service = make_service()
    narrative = await service.create("My Narrative")
    actor = await service.add_actor(narrative.id, "Max", ActorType.INDIVIDUAL)  # type: ignore[arg-type]

    with pytest.raises(ActorValidationError):
        await service.update_actor(narrative.id, actor.id, "", ActorType.INDIVIDUAL, None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# remove_actor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_remove_actor_removes_actor_from_narrative() -> None:
    """Expects the actor to be absent from the narrative after remove_actor is called."""
    service = make_service()
    narrative = await service.create("My Narrative")
    actor = await service.add_actor(narrative.id, "Max", ActorType.INDIVIDUAL)  # type: ignore[arg-type]
    assert actor.id is not None

    await service.remove_actor(narrative.id, actor.id)  # type: ignore[arg-type]

    updated_narrative = await service.find_by_id(narrative.id)  # type: ignore[arg-type]
    assert not any(a.id == actor.id for a in updated_narrative.actors)


@pytest.mark.asyncio
async def test_narrative_service_remove_actor_raises_for_unknown_narrative_id() -> None:
    """Expects NarrativeNotFoundError when the narrative does not exist."""
    service = make_service()

    with pytest.raises(NarrativeNotFoundError):
        await service.remove_actor("00000000-0000-0000-0000-000000000000", "actor-id")


@pytest.mark.asyncio
async def test_narrative_service_remove_actor_raises_for_unknown_actor_id() -> None:
    """Expects ActorNotFoundError when the actor does not exist in the narrative."""
    service = make_service()
    narrative = await service.create("My Narrative")

    with pytest.raises(ActorNotFoundError):
        await service.remove_actor(narrative.id, "00000000-0000-0000-0000-000000000000")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# list_for_user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_list_for_user_returns_narratives_for_user() -> None:
    """Expects list_for_user() to return only narratives owned by the given user."""
    from api.models.narrative import Narrative
    from tests.fakes.fake_user_repository import DEFAULT_USER_ID

    repository = FakeNarrativeRepository()
    service = make_service(repository=repository)

    narrative = Narrative.create("User Narrative")
    narrative.assign_user(DEFAULT_USER_ID)
    await repository.save(narrative)

    results = await service.list_for_user(DEFAULT_USER_ID)
    assert len(results) == 1
    assert results[0].title == "User Narrative"


@pytest.mark.asyncio
async def test_narrative_service_create_assigns_user_id() -> None:
    """Expects create() with user_id to assign that user to the narrative."""
    from tests.fakes.fake_user_repository import DEFAULT_USER_ID

    service = make_service()
    narrative = await service.create("New Narrative", user_id=DEFAULT_USER_ID)
    assert narrative.user_id == DEFAULT_USER_ID


@pytest.mark.asyncio
async def test_narrative_service_import_assigns_user_id() -> None:
    """Expects import_from_file() with user_id to assign that user to the narrative."""
    import os
    import tempfile

    from tests.fakes.fake_user_repository import DEFAULT_USER_ID

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test\nContent")
        path = Path(f.name)
    try:
        service = make_service()
        narrative = await service.import_from_file(path, user_id=DEFAULT_USER_ID)
        assert narrative.user_id == DEFAULT_USER_ID
    finally:
        os.unlink(str(path))


# ---------------------------------------------------------------------------
# link_to_causal_model
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_link_to_causal_model_returns_narrative_with_id() -> None:
    """Expects link_to_causal_model to return the Narrative with its existing ID."""
    service = make_service()
    narrative = await service.create("My Narrative")

    updated = await service.link_to_causal_model(narrative.id, "model-xyz")  # type: ignore[arg-type]

    assert updated.id == narrative.id


@pytest.mark.asyncio
async def test_narrative_service_link_to_causal_model_stores_causal_model_id() -> None:
    """Expects the causal_model_id to be accessible on the returned narrative."""
    service = make_service()
    narrative = await service.create("My Narrative")

    updated = await service.link_to_causal_model(narrative.id, "model-xyz")  # type: ignore[arg-type]

    assert updated.causal_model_id == "model-xyz"


@pytest.mark.asyncio
async def test_narrative_service_link_to_causal_model_raises_for_unknown_narrative_id() -> None:
    """Expects NarrativeNotFoundError when the narrative does not exist."""
    service = make_service()

    with pytest.raises(NarrativeNotFoundError):
        await service.link_to_causal_model("00000000-0000-0000-0000-000000000000", "model-xyz")


@pytest.mark.asyncio
async def test_narrative_service_link_to_causal_model_raises_for_empty_id() -> None:
    """Expects NarrativeValidationError when the causal model ID is empty."""
    from api.exceptions.narrative import NarrativeValidationError

    service = make_service()
    narrative = await service.create("My Narrative")

    with pytest.raises(NarrativeValidationError):
        await service.link_to_causal_model(narrative.id, "")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# list_summaries_for_user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_summaries_for_user_returns_counts() -> None:
    """Expects list_summaries_for_user to return NarrativeSummary with scene/actor/claim counts."""
    from api.models.narrative import Narrative, NarrativeSummary, Scene
    from api.tests.fakes.fake_narrative_repository import FakeNarrativeRepository
    from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID

    repo = FakeNarrativeRepository()
    n = Narrative.create("Test")
    n.assign_user(DEFAULT_USER_ID)
    saved = await repo.save(n)
    scene = Scene.create(title="Scene 1", text="Text", position=0)
    await repo.add_scene(saved.id, scene)  # type: ignore[arg-type]

    service = make_service(repository=repo)
    summaries = await service.list_summaries_for_user(DEFAULT_USER_ID)

    assert len(summaries) == 1
    assert isinstance(summaries[0], NarrativeSummary)
    assert summaries[0].title == "Test"
    assert summaries[0].scene_count == 1
    assert summaries[0].actor_count == 0
    assert summaries[0].claim_count == 0
