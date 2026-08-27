from lat_ces.scientific.ontology import (
    ALLOWED_RELATION_TYPES,
    OntologyGraph,
    ScientificEntity,
    ScientificRelation,
)

OntologyEntity = ScientificEntity
OntologyRelation = ScientificRelation

class Ontology(OntologyGraph):
    """Backward-compatible facade over the canonical SCI-0062 ontology graph."""
    def __init__(self, *, ontology_id: str | None = None, version: int = 1) -> None:
        super().__init__()
        if version < 1:
            raise ValueError("Ontology version must be >= 1")
        self.ontology_id = ontology_id or "ONTO-CANONICAL"
        self.version = version

    def relate(self, source_id: str, relation: str, target_id: str) -> OntologyRelation:
        item = OntologyRelation(source_id, relation, target_id)
        return self.add_relation(item)

    def get(self, entity_id: str):
        return self.entities.get(entity_id)

    def relations(self):
        return tuple(self.relations)

    def entities_list(self):
        return tuple(self.entities.values())
