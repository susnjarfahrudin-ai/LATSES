from lat_ces.catalog.evidence_status import EvidenceState, presentation_evidence_state
from lat_ces.gui_product_catalog import ProductCatalogMixin
from lat_ces.gui_presentation import Scene1PresentationExtension, Scene2PresentationExtension
from lat_ces.gui_scene1 import Scene1CompleteBuildingWorkspaceApp


def test_production_gui_has_one_explicit_scene_presentation_path() -> None:
    assert "_scene1_presentation" in Scene1CompleteBuildingWorkspaceApp.__init__.__code__.co_names
    assert "_scene2_presentation" in Scene1CompleteBuildingWorkspaceApp.__init__.__code__.co_names
    assert "BuildingVisualizationAdapter" not in Scene1CompleteBuildingWorkspaceApp.show_scene1.__code__.co_names
    assert "PresentationController" not in Scene1CompleteBuildingWorkspaceApp.show_scene1.__code__.co_names


def test_presentation_extensions_are_explicit_and_model_agnostic() -> None:
    assert "render" in Scene1PresentationExtension.__dict__
    assert "export" in Scene2PresentationExtension.__dict__
    assert "BuildingModel" not in Scene1PresentationExtension.__doc__
    assert "BuildingModel" not in Scene2PresentationExtension.__doc__


def test_catalog_declaration_does_not_admit_material_to_building_model() -> None:
    names = ProductCatalogMixin._add_catalog_material.__code__.co_names
    assert "add_material" not in names
    assert "_user_product_catalog" in names


def test_evidence_states_are_not_silently_upgraded() -> None:
    assert presentation_evidence_state("USER_DECLARED") is EvidenceState.DECLARED
    assert presentation_evidence_state("REFERENCE") is EvidenceState.DECLARED
    assert presentation_evidence_state("MISSING") is EvidenceState.INPUT_REQUIRED
    assert presentation_evidence_state("VERIFIED") is EvidenceState.VERIFIED
    assert presentation_evidence_state("ACCEPTED_FOR_CALCULATION") is EvidenceState.ACCEPTED_FOR_CALCULATION
    assert presentation_evidence_state("REJECTED") is EvidenceState.REJECTED
    assert presentation_evidence_state("USER_DECLARED") is not EvidenceState.VERIFIED
