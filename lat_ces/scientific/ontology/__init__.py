from .entity import ScientificEntity
from .domain import ScientificDomain
from .definition import ScientificDefinition
from .relation import ALLOWED_RELATION_TYPES, ScientificRelation
from .ontology_graph import OntologyGraph
from .consistency import validate_entity, validate_relation, validate_graph
from .versioning import OntologyRevision

__all__ = [
    "ScientificEntity", "ScientificDomain", "ScientificDefinition",
    "ScientificRelation", "ALLOWED_RELATION_TYPES", "OntologyGraph",
    "validate_entity", "validate_relation", "validate_graph", "OntologyRevision",
]
