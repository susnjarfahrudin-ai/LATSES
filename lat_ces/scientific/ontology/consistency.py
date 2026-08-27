from __future__ import annotations
from .entity import ScientificEntity
from .ontology_graph import OntologyGraph
from .relation import ScientificRelation

def validate_entity(entity: ScientificEntity) -> bool:
    return bool(entity.entity_id and entity.name.strip() and entity.entity_type.strip() and entity.definition.strip() and entity.domain.strip())

def validate_relation(relation: ScientificRelation, graph: OntologyGraph) -> bool:
    return relation.source_id in graph.entities and relation.target_id in graph.entities

def validate_graph(graph: OntologyGraph) -> bool:
    seen: set[str] = set()
    for entity in graph.entities.values():
        if entity.entity_id in seen or not validate_entity(entity):
            return False
        seen.add(entity.entity_id)
    return all(validate_relation(r, graph) for r in graph.relations)
