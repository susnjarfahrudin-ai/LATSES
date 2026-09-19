"""Verified-only experience/baseline learning."""
from __future__ import annotations
from dataclasses import dataclass
from statistics import mean,pstdev
from typing import Iterable

@dataclass(frozen=True)
class BaselineStats:
    count:int; mean:float; sigma:float; p95:float; p99:float

class VerifiedBaseline:
    def __init__(self): self._samples: list[float]=[]
    @staticmethod
    def _percentile(values, p):
        if not values: return 0.0
        xs=sorted(values); pos=(len(xs)-1)*p; lo=int(pos); hi=min(lo+1,len(xs)-1); frac=pos-lo
        return xs[lo]+(xs[hi]-xs[lo])*frac
    def observe(self, value: float, *, trusted: bool, normal: bool) -> bool:
        if trusted and normal and value >= 0:
            self._samples.append(float(value)); return True
        return False
    def stats(self) -> BaselineStats:
        return BaselineStats(len(self._samples),mean(self._samples) if self._samples else 0.0,pstdev(self._samples) if len(self._samples)>1 else 0.0,self._percentile(self._samples,.95),self._percentile(self._samples,.99))
    def expected(self,k:float=3.0)->float:
        s=self.stats(); return s.mean+k*s.sigma
    def samples(self)->tuple[float,...]: return tuple(self._samples)
