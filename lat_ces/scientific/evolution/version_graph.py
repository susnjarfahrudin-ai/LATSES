from __future__ import annotations

class KnowledgeVersionGraph:
    def __init__(self) -> None:
        self.graph: dict[str, str | None] = {}

    def add_version(self, version: str, parent: str | None = None) -> None:
        if not version.strip():
            raise ValueError("Knowledge version requires identity")
        if version in self.graph and self.graph[version] != parent:
            raise ValueError(f"Version already registered with another parent: {version}")
        if parent is not None and parent not in self.graph:
            raise ValueError(f"Unknown parent version: {parent}")
        self.graph[version] = parent

    def parent_of(self, version: str) -> str | None:
        return self.graph.get(version)
