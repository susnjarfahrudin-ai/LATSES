from lat_ces.scientific.ontology import (
    ALLOWED_RELATION_TYPES,
    OntologyGraph,
    ScientificEntity,
    ScientificRelation,
)

OntologyEntity = ScientificEntity
OntologyRelation = ScientificRelation

class Ontology:
    """Backward-compatible facade over the canonical SCI-0062 ontology graph."""
    def __init__(self, *, ontology_id: str | None = None, version: int = 1) -> None:
        if version < 1:
            raise ValueError("Ontology version must be >= 1")
        self.ontology_id = ontology_id or "ONTO-CANONICAL"
        self.version = version
        self._graph = OntologyGraph()

    def add_entity(self, entity: OntologyEntity) -> OntologyEntity:
        return self._graph.add_entity(entity)

    def relate(self, source_id: str, relation: str, target_id: str) -> OntologyRelation:
        return self._graph.add_relation(OntologyRelation(source_id, relation, target_id))

    def get(self, entity_id: str):
        return self._graph.entities.get(entity_id)

    def relations(self) -> tuple[OntologyRelation, ...]:
        return tuple(self._graph.relations)

    def entities(self) -> tuple[OntologyEntity, ...]:
        return tuple(self._graph.entities.values())

    def validate(self):
        from lat_ces.scientific.ontology.consistency import validate_graph
        if not validate_graph(self._graph):
            raise ValueError("Ontology consistency validation failed")
        return self
