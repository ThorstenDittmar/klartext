"""SceneMother — builds Scene test objects for all test scenarios."""

from __future__ import annotations

from api.models.narrative import Scene


class SceneMother:
    """Factory for Scene test objects.

    Use minimal() for tests that only need a valid scene.
    Use at_position(n) when position matters.
    Use collection() for tests that need multiple varied scenes.
    """

    @staticmethod
    def minimal() -> Scene:
        """Simplest valid scene — one sentence, position 1."""
        return Scene.create(
            title="Szene 1",
            text="Es war einmal.",
            position=1,
        )

    @staticmethod
    def at_position(position: int) -> Scene:
        """Valid scene at a specific position — for ordering tests."""
        return Scene.create(
            title=f"Szene {position}",
            text=f"Inhalt der Szene an Position {position}.",
            position=position,
        )

    @staticmethod
    def with_rich_text() -> Scene:
        """Scene with a longer, more realistic text — for parsing and extraction tests."""
        return Scene.create(
            title="Szene 1",
            text=(
                "Der Abend, an dem sie aufgehört hatten, miteinander zu reden, "
                "war kein besonderer Abend gewesen. Es war ein Dienstag im Februar, "
                "irgendwo zwischen dem dritten Lockdown und der Debatte über die Impfpflicht. "
                "Mara hatte einfach ihren Laptop zugeklappt und gesagt: Ich kann nicht mehr."
            ),
            position=1,
        )

    @staticmethod
    def collection() -> list[Scene]:
        """Three varied scenes — for tests that need a realistic scene list."""
        return [
            Scene.create(title="Szene 1", text="Erster Akt: Der Konflikt beginnt.", position=1),
            Scene.create(title="Szene 2", text="Zweiter Akt: Die Wendung.", position=2),
            Scene.create(title="Szene 3", text="Dritter Akt: Die Auflösung.", position=3),
        ]
