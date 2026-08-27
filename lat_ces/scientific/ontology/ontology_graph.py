from __future__ import annotations
from dataclasses import dataclass, field
from .entity import ScientificEntity
from .relation import ScientificRelation

@dataclass
class OntologyGraph:
    entities: dict[str, ScientificEntity] = field(default_factory=dict)
    relations: list[ScientificRelation] = field(default_factory=list)

    def add_entity(self, entity: ScientificEntity) -> ScientificEntity:
        existing = self.entities.get(entity.entity_id)
        if existing is not None and existing != entity:
            raise ValueError(f"Duplicate entity identity: {entity.entity_id}")
        self.entities[entity.entity_id] = entity
        return entity

    def add_relation(self, relation: ScientificRelation) -> ScientificRelation:
        if relation.source_id not in self.entities or relation.target_id not in self.entities:
            raise ValueError("Relation endpoints must exist in ontology graph")
        if relation not in self.relations:
            self.relations.append(relation)
        return relation

    def related(self, source_id: str) -> tuple[ScientificRelation, ...]:
        return tuple(r for r in self.relations if r.source_id == source_id)
