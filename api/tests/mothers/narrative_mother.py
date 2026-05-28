"""NarrativeMother — builds Narrative test objects for all test scenarios."""

from __future__ import annotations

from api.models.narrative import Actor, ActorType, Narrative, Scene
from tests.mothers.scene_mother import SceneMother


class NarrativeMother:
    """Factory for Narrative test objects.

    Use empty() for tests that only need a valid narrative container.
    Use with_two_scenes() for the most common case — a narrative with content.
    Use complete() for serialisation, mapping and full-stack tests.
    Use collection() for list, filter and pagination tests.
    """

    @staticmethod
    def empty() -> Narrative:
        """Simplest valid narrative — no scenes, title only."""
        return Narrative.create(title="Klartext")

    @staticmethod
    def with_one_scene() -> Narrative:
        """Narrative with a single scene — for minimal content tests."""
        narrative = Narrative.create(title="Klartext")
        narrative.add_scene(SceneMother.minimal())
        return narrative

    @staticmethod
    def with_two_scenes() -> Narrative:
        """Narrative with two scenes — the standard test case for most service and repo tests."""
        narrative = Narrative.create(title="Klartext")
        narrative.add_scene(SceneMother.at_position(1))
        narrative.add_scene(SceneMother.at_position(2))
        return narrative

    @staticmethod
    def complete() -> Narrative:
        """Fully populated narrative with three varied scenes — for serialisation and mapping tests."""
        narrative = Narrative.create(title="Klartext – Eine Geschichte über eine Geschichte")
        for scene in SceneMother.collection():
            narrative.add_scene(scene)
        return narrative

    @staticmethod
    def with_title(title: str) -> Narrative:
        """Narrative with a custom title — for title-specific tests."""
        return Narrative.create(title=title)

    @staticmethod
    def with_actors() -> Narrative:
        """Narrative with one scene and three actors of different types — for actor-related tests."""
        narrative = Narrative.create(title="Klartext")
        narrative.add_scene(SceneMother.minimal())
        narrative.add_actor(Actor.create(name="Max", typ=ActorType.INDIVIDUAL))
        narrative.add_actor(Actor.create(name="CDU", typ=ActorType.ORGANISATION))
        narrative.add_actor(Actor.create(name="Voters", typ=ActorType.GROUP))
        return narrative

    @staticmethod
    def linked_to_causal_model(causal_model_id: str) -> Narrative:
        """Narrative with a CausalModel link — for consistency checking and Transparenzbericht tests."""
        narrative = Narrative.create(title="Klartext")
        narrative.add_scene(SceneMother.minimal())
        narrative.link_to_causal_model(causal_model_id)
        return narrative

    @staticmethod
    def collection() -> list[Narrative]:
        """Three narratives with distinct titles — for list, filter and pagination tests."""
        titles = ["Erstes Narrativ", "Zweites Narrativ", "Drittes Narrativ"]
        narratives = []
        for title in titles:
            n = Narrative.create(title=title)
            n.add_scene(Scene.create(title="Szene 1", text=f"Inhalt von {title}.", position=1))
            narratives.append(n)
        return narratives
