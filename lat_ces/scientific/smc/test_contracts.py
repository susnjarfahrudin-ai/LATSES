from .contracts import ScientificModelContract
from .registry import SMCRegistry

def test_model_contract_roundtrip():
    model = ScientificModelContract(
        "SMC-MODEL-0001",
        "Reference model",
        "1.0",
        "neutral",
        "defined scope",
        inputs={"x": "quantity"},
        outputs={"y": "quantity"},
        units={"x": "1", "y": "1"},
    )
    registry = SMCRegistry()
    registry.register(model)
    assert registry.get("SMC-MODEL-0001", "1.0") is model
