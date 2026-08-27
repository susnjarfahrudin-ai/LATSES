import json
import hashlib
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Dict, Tuple, Any

class HardenedDimension:
    CANONICAL_ORDER=["M","L","T","I","Θ","N","J"]
    def __init__(self,name,symbols):
        if not name: raise ValueError("Dimension requires an explicit identifier name.")
        cleaned={k:v for k,v in symbols.items() if k in self.CANONICAL_ORDER and v!=0}
        self._name=name; self._symbols=MappingProxyType({k:cleaned[k] for k in self.CANONICAL_ORDER if k in cleaned})
    @property
    def name(self): return self._name
    @property
    def symbols(self): return self._symbols
    def __mul__(self,other):
        combined=dict(self._symbols)
        for k,v in other.symbols.items(): combined[k]=combined.get(k,0)+v
        return HardenedDimension(f"({self._name}*{other.name})",combined)
    def __truediv__(self,other):
        combined=dict(self._symbols)
        for k,v in other.symbols.items(): combined[k]=combined.get(k,0)-v
        return HardenedDimension(f"({self._name}/{other.name})",combined)
    def __eq__(self,other): return isinstance(other,HardenedDimension) and dict(self._symbols)==dict(other.symbols)
    def __str__(self): return "Dimensionless [1]" if not self._symbols else " ".join(f"{k}^{v}" if v!=1 else k for k,v in self._symbols.items())

MASS=HardenedDimension("Mass",{"M":1}); LENGTH=HardenedDimension("Length",{"L":1}); TIME=HardenedDimension("Time",{"T":1}); TEMPERATURE=HardenedDimension("Temperature",{"Θ":1}); AMOUNT=HardenedDimension("Amount of Substance",{"N":1})
AREA=LENGTH*LENGTH; VOLUME=AREA*LENGTH; DENSITY=MASS/VOLUME; VELOCITY=LENGTH/TIME; ACCELERATION=VELOCITY/TIME
FORCE=MASS*acceleration if 'acceleration' in globals() else MASS*(LENGTH/(TIME*TIME))
PRESSURE=HardenedDimension("Pressure",{"M":1,"L":-1,"T":-2}); ENERGY=HardenedDimension("Energy/Work/Heat",{"M":1,"L":2,"T":-2}); SPECIFIC_HEAT=HardenedDimension("Specific Heat Capacity",{"L":2,"T":-2,"Θ":-1}); THERMAL_CONDUCTIVITY=HardenedDimension("Thermal Conductivity",{"M":1,"L":1,"T":-3,"Θ":-1}); DYNAMIC_VISCOSITY=HardenedDimension("Dynamic Viscosity",{"M":1,"L":-1,"T":-1})

class HardenedSKO:
    def __init__(self,sko_id,name,domain,definition,assumptions,limitations,payload):
        self._locked=False; self._sko_id=sko_id; self._name=name; self._domain=domain; self._definition=definition; self._assumptions=tuple(assumptions); self._limitations=tuple(limitations); self._payload=MappingProxyType(dict(payload)); self._timestamp=datetime.now(timezone.utc).isoformat(); self._signature=self._calculate_deterministic_hash(); self._locked=True
    @property
    def name(self): return self._name
    @property
    def assumptions(self): return self._assumptions
    @property
    def signature(self): return self._signature
    def _calculate_deterministic_hash(self):
        serialized={"sko_id":self._sko_id,"name":self._name,"domain":self._domain,"definition":self._definition,"assumptions":self._assumptions,"limitations":self._limitations,"payload":dict(self._payload)}
        return hashlib.sha256(json.dumps(serialized,sort_keys=True).encode("utf-8")).hexdigest()
    def __setattr__(self,key,value):
        if hasattr(self,"_locked") and self._locked: raise AttributeError("Released ScientificKnowledgeObject state is immutable.")
        super().__setattr__(key,value)

class HardenedThermodynamicsEngine:
    UNIVERSAL_GAS_CONSTANT=8.314462618
    @staticmethod
    def compute_ideal_gas_pressure(substance_amount_moles,temp_kelvin,volume_cubic_meters):
        if volume_cubic_meters<=0: raise ValueError("Volume must be positive.")
        if temp_kelvin<0: raise ValueError("Absolute temperature cannot be below 0 K.")
        return (substance_amount_moles*HardenedThermodynamicsEngine.UNIVERSAL_GAS_CONSTANT*temp_kelvin)/volume_cubic_meters
    @staticmethod
    def compute_conduction_heat_flux(thermal_cond,thickness_meters,temp_high,temp_low):
        if thickness_meters<=0: raise ValueError("Thickness must be positive.")
        return thermal_cond*(temp_high-temp_low)/thickness_meters

class HardenedFluidMechanicsEngine:
    STANDARD_GRAVITY=9.80665
    @staticmethod
    def compute_hydrostatic_pressure(density_kg_m3,depth_meters,surface_pressure_pascal=101325.0):
        if density_kg_m3<0 or depth_meters<0: raise ValueError("Negative fluid metrics are invalid.")
        return surface_pressure_pascal+density_kg_m3*HardenedFluidMechanicsEngine.STANDARD_GRAVITY*depth_meters
    @staticmethod
    def compute_reynolds_number(density_kg_m3,velocity_m_s,characteristic_length_m,dynamic_visc_pa_s):
        if dynamic_visc_pa_s<=0: raise ValueError("Dynamic viscosity must be positive.")
        return density_kg_m3*velocity_m_s*characteristic_length_m/dynamic_visc_pa_s

def execute_domain_extension_verification_suite():
    assert dict(PRESSURE.symbols)=={"M":1,"L":-1,"T":-2}
    sko=HardenedSKO("LAT-SKO-THERMO-0001","Ideal Gas Reference Profile","Thermodynamics","Constitutional tracking profile",("Ideal gas behavior",),("Low pressure domains",),{"gas":"N2","pressure_pa":101325.0})
    try: sko.name="Malicious Override Attempt"; return False
    except AttributeError: pass
    assert sko.signature==sko._calculate_deterministic_hash()
    calc_p=HardenedThermodynamicsEngine.compute_ideal_gas_pressure(10.0,300.0,0.5); assert abs(calc_p-(10.0*8.314462618*300.0/0.5))<1e-9
    assert HardenedFluidMechanicsEngine.compute_reynolds_number(1000.0,2.0,0.05,0.001)==100000.0
    return True
