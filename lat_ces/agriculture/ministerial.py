"""Official agriculture data and evolution views for the ministerial workspace."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgricultureIndicator:
    scope: str
    metric: str
    value: str
    period: str
    source: str
    source_url: str
    note: str


@dataclass(frozen=True)
class AgricultureEvolution:
    scope: str
    indicator: str
    period: str
    evolution: str
    source: str
    source_url: str
    interpretation: str


@dataclass(frozen=True)
class AgricultureSnapshot:
    title: str
    indicators: tuple[AgricultureIndicator, ...]
    evolution: tuple[AgricultureEvolution, ...]

    def for_scope(self, scope: str) -> tuple[AgricultureIndicator, ...]:
        return tuple(x for x in self.indicators if x.scope == scope)

    def evolution_for(self, scope: str) -> tuple[AgricultureEvolution, ...]:
        return tuple(x for x in self.evolution if x.scope == scope)


SOURCES = {
    "BiH prices": "https://bhas.gov.ba/data/Publikacije/Saopstenja/2026/AGR_23_2025_Y1_1_BS.pdf",
    "BiH purchase": "https://bhas.gov.ba/data/Publikacije/Saopstenja/2026/AGR_08_2025_Y1_1_HR.pdf",
    "BiH crops": "https://bhas.gov.ba/data/Publikacije/Bilteni/2025/NUM_00_2024_TB_1_EN.pdf",
    "EU output": "https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251107-1",
    "EU trade": "https://ec.europa.eu/eurostat/en/web/products-eurostat-news/w/ddn-20260512-2",
    "EU livestock": "https://ec.europa.eu/eurostat/en/web/products-eurostat-news/w/ddn-20260630-2",
    "FAO trade": "https://www.fao.org/markets-and-trade/home/the-state-of-agricultural-commodity-markets-%28soco%29-2026---trade--resilience-and-food-security/en",
    "FAO food outlook": "https://www.fao.org/markets-and-trade/",
}


def build_official_snapshot() -> AgricultureSnapshot:
    indicators = (
        AgricultureIndicator("BiH", "Cijene poljoprivrednih proizvoda", "+52,4%", "2025 prema prosjeku 2020", "Agencija za statistiku BiH", SOURCES["BiH prices"], "Biljna proizvodnja +49,9%; stočna proizvodnja +55,9%."),
        AgricultureIndicator("BiH", "Otkup žitarica", "+27,6%", "2025 prema 2024", "Agencija za statistiku BiH", SOURCES["BiH purchase"], "Vrijednost otkupa."),
        AgricultureIndicator("BiH", "Otkup voća", "-16,9%", "2025 prema 2024", "Agencija za statistiku BiH", SOURCES["BiH purchase"], "Vrijednost otkupa."),
        AgricultureIndicator("BiH", "Kukuruz za zrno", "720 hilj. t", "2023/2024", "Agencija za statistiku BiH", SOURCES["BiH crops"], "103 hilj. ha; 7,0 t/ha."),
        AgricultureIndicator("BiH", "Pšenica", "247 hilj. t", "2023/2024", "Agencija za statistiku BiH", SOURCES["BiH crops"], "57 hilj. ha; 4,3 t/ha."),
        AgricultureIndicator("EU", "Vrijednost poljoprivredne proizvodnje", "€531,9 mlrd", "2024", "Eurostat", SOURCES["EU output"], "2024 je bilo -0,9% prema 2023, nakon vrha vrijednosti u 2022."),
        AgricultureIndicator("EU", "Izvoz poljoprivrednih proizvoda", "€238,2 mlrd", "2025", "Eurostat", SOURCES["EU trade"], "2025: +1,6% prema 2024."),
        AgricultureIndicator("EU", "Uvoz poljoprivrednih proizvoda", "€213,5 mlrd", "2025", "Eurostat", SOURCES["EU trade"], "2025: +9,3% prema 2024."),
        AgricultureIndicator("EU", "Trgovinski saldo poljoprivrede", "+€24,7 mlrd", "2025", "Eurostat", SOURCES["EU trade"], "Izvoz minus uvoz."),
        AgricultureIndicator("EU", "Goveda", "71,6 miliona", "2025", "Eurostat", SOURCES["EU livestock"], "U odnosu na 2015: -9,7%."),
        AgricultureIndicator("EU", "Svinje", "131,5 miliona", "2025", "Eurostat", SOURCES["EU livestock"], "U odnosu na 2015: -8,9%."),
        AgricultureIndicator("Svijet", "Trgovina hranom i poljoprivredom", "5×", "2000 → 2024", "FAO", SOURCES["FAO trade"], "Vrijednost trgovine porasla je petostruko."),
        AgricultureIndicator("Svijet", "Globalne žitarice", "historijski visoki nivoi", "2026 outlook", "FAO", SOURCES["FAO food outlook"], "FAO očekuje ublažavanje proizvodnje sa rekordnih nivoa, ali ostanak na historijski visokim nivoima."),
    )
    evolution = (
        AgricultureEvolution("BiH", "Cijene poljoprivrede", "2020 → 2025", "+52,4%", "Agencija za statistiku BiH", SOURCES["BiH prices"], "Dugoročniji pomak cijena mjeri se prema prosjeku 2020."),
        AgricultureEvolution("BiH", "Vrijednost otkupa žitarica", "2024 → 2025", "+27,6%", "Agencija za statistiku BiH", SOURCES["BiH purchase"], "Rast vrijednosti otkupa žitarica."),
        AgricultureEvolution("BiH", "Vrijednost otkupa voća", "2024 → 2025", "-16,9%", "Agencija za statistiku BiH", SOURCES["BiH purchase"], "Pad vrijednosti otkupa voća."),
        AgricultureEvolution("EU", "Poljoprivredna proizvodnja po vrijednosti", "2023 → 2024", "-0,9%", "Eurostat", SOURCES["EU output"], "Nominalna vrijednost pala je uz +1,0% volumena i -1,8% nominalne cijene."),
        AgricultureEvolution("EU", "Poljoprivredni izvoz", "2015 → 2025", "prosječno +4,4% godišnje", "Eurostat", SOURCES["EU trade"], "Dugoročni rast vrijednosti izvoza."),
        AgricultureEvolution("EU", "Poljoprivredni uvoz", "2015 → 2025", "prosječno +5,0% godišnje", "Eurostat", SOURCES["EU trade"], "Uvoz je rastao brže od izvoza na toj desetogodišnjoj osnovi."),
        AgricultureEvolution("EU", "Broj svinja", "2015 → 2025", "-8,9%", "Eurostat", SOURCES["EU livestock"], "Dugoročni pad populacije svinja."),
        AgricultureEvolution("EU", "Broj goveda", "2015 → 2025", "-9,7%", "Eurostat", SOURCES["EU livestock"], "Dugoročni pad populacije goveda."),
        AgricultureEvolution("Svijet", "Trgovina hranom i poljoprivredom", "2000 → 2024", "5× veća", "FAO", SOURCES["FAO trade"], "Veća integracija zemalja niskog i srednjeg dohotka u globalna tržišta."),
        AgricultureEvolution("Svijet", "Žitarice", "2026 outlook", "blago ispod rekorda, ali historijski visoko", "FAO", SOURCES["FAO food outlook"], "Ovo je outlook, ne realizovani istorijski podatak."),
    )
    return AgricultureSnapshot("Poljoprivreda — službeni pregled i evolucija", indicators, evolution)


__all__ = [
    "AgricultureEvolution",
    "AgricultureIndicator",
    "AgricultureSnapshot",
    "SOURCES",
    "build_official_snapshot",
]
