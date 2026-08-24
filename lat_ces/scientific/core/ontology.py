from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
from uuid import uuid4


@dataclass(frozen=True)
class OntologyRelation:
    source_id: str
    relation: str
    target_id: str


@dataclass(frozen=True)
class OntologyEntity:
    entity_id: str
    entity_type: str
    domain: str
    definition: str
    version: int = 1
    relations: tuple[OntologyRelation, ...] = field(default_factory=tuple)
    provenance: str | None = None


class Ontology:
    """Canonical SCI ontology graph with explicit identity and relations."""

    def __init__(self, *, ontology_id: str | None = None, version: int = 1) -> None:
        self.ontology_id = ontology_id or f"ONTO-{uuid4().hex.upper()}"
        self.version = version
        self._entities: dict[str, OntologyEntity] = {}
        self._relations: set[OntologyRelation] = set()

    def add_entity(self, entity: OntologyEntity) -> OntologyEntity:
        if not entity.entity_id.strip():
            raise ValueError("Ontology entity requires identity")
        if not entity.entity_type.strip() or not entity.domain.strip():
            raise ValueError("Ontology entity requires type and domain")
        if not entity.definition.strip():
            raise ValueError("Ontology entity requires definition")
        existing = self._entities.get(entity.entity_id)
        if existing is not None and existing != entity:
            raise ValueError(f"Ontology identity collision: {entity.entity_id}")
        self._entities[entity.entity_id] = entity
        self._relations.update(entity.relations)
        return entity

    def relate(self, source_id: str, relation: str, target_id: str) -> OntologyRelation:
        if source_id not in self._entities or target_id not in self._entities:
            raise ValueError("Ontology relation requires existing source and target entities")
        if not relation.strip():
            raise ValueError("Ontology relation requires a name")
        item = OntologyRelation(source_id, relation, target_id)
        self._relations.add(item)
        return item

    def get(self, entity_id: str) -> OntologyEntity | None:
        return self._entities.get(entity_id)

    def relations(self) -> tuple[OntologyRelation, ...]:
        return tuple(sorted(self._relations, key=lambda r: (r.source_id, r.relation, r.target_id)))

    def entities(self) -> tuple[OntologyEntity, ...]:
        return tuple(self._entities.values())

    def validate(self) -> "Ontology":
        for relation in self._relations:
            if relation.source_id not in self._entities or relation.target_id not in self._entities:
                raise ValueError("Ontology contains dangling relation")
        return self
