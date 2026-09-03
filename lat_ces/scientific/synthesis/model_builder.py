from __future__ import annotations

class ScientificModelBuilder:
    def build(self, knowledge_objects: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
        if not knowledge_objects:
            raise ValueError("No input knowledge")
        return {"components": tuple(knowledge_objects)}
