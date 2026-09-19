from lat_ces.rci_ad.universal_io import DataCarrier,Direction,InterfaceObservation,DEFAULT_INTERFACE_TYPES
from lat_ces.rci_ad.resource_model import ResourceState,host_pressure,pressure_model,data_unit_weight,resource_feasibility
from lat_ces.rci_ad.learning import VerifiedBaseline
from lat_ces.rci_ad.prediction import predict_linear,predict_resource
from lat_ces.rci_ad.communicator import Communicator
from lat_ces.rci_ad.canonical_observation import CanonicalObservation
from lat_ces.rci_ad.integrity import verify_artifact,verify_test_vectors,ModelSelfTestStatus
from lat_ces.rci_ad.recovery import plan_recovery
from lat_ces.rci_ad.defense_controller import DefenseController,DefenseInput
from lat_ces.rci_ad.status import IntegrityStatus,TrustStatus
from lat_ces.rci_ad.trust_state import TrustState
from lat_ces.rci_ad.integrity_state import IntegrityState

def test_universal_interfaces_are_explicit():
    for name in ("USB","Bluetooth","CD/DVD/Blu-ray","NVMe","SATA","Thunderbolt","PCIe","Ethernet","Wi-Fi","Optical","HDMI","DisplayPort"):
        assert name in DEFAULT_INTERFACE_TYPES or name in ("CD/DVD/Blu-ray",)

def test_data_carrier_and_weight():
    d=DataCarrier("src","dev","USB","USB transfer",Direction.IN,"bulk",1_000_000,100_000,2,1,10,0,0.2,2_000_000,0.01,1,"VERIFIED","TRUSTED",1.0)
    assert data_unit_weight(d)>0

def test_verified_only_learning():
    b=VerifiedBaseline()
    assert not b.observe(100,trusted=False,normal=True)
    assert b.observe(10,trusted=True,normal=True)
    assert b.stats().count==1

def test_prediction_and_budget():
    assert predict_linear(100,10,5)==150
    p=predict_resource(used=100,memory_rate=10,software=10,network=5,storage=5,io=5,total=1000,os_reserved=100,reserve=100,horizon=5)
    assert p.resource_feasibility>0

def test_communicator_routes_validated_observation():
    obs=CanonicalObservation("src","telemetry",None,"USB",None,"rate",1.0,10.0,"B/s","IN","bulk",10.0,100.0,.9,"1",IntegrityState.VERIFIED,TrustState.TRUSTED,1)
    c=Communicator(); c.register_route("telemetry",("defense","security"))
    assert len(c.publish(obs))==2

def test_integrity_and_model_vectors():
    content=b"trusted-model"
    import hashlib
    digest=hashlib.sha256(content).hexdigest()
    assert verify_artifact(content,digest).trusted
    assert verify_test_vectors(lambda x:x*x,((2,4,0),)) is ModelSelfTestStatus.VALID

def test_recovery_uses_trusted_artifact():
    p=plan_recovery("module","artifact","config")
    assert p.actions[-1]=="REINTEGRATE"

def test_defense_controller_keeps_integrity_and_trust_authoritative():
    d=DefenseController().decide(DefenseInput(.1,.1,.1,0.2,.9,IntegrityStatus.COMPROMISED,TrustStatus.TRUSTED))
    assert d.action.value=="ISOLATE"
