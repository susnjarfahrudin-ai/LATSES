"""Unified Building Engineering workspace for LAT-CES.

UI-first workspace around one BuildingModel. It exposes drafting, airflow,
building systems, analysis and AI-advisor concepts without creating a second
source of geometry or pretending that placeholder values are final results.
"""
from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from .architecture_visualization import EngineeringArchitectureView


@dataclass(frozen=True)
class EngineeringModule:
    key: str
    title: str
    icon: str
    description: str
    status: str = "MODEL READY"


ENGINEERING_MODULES = (
    EngineeringModule("model", "Objekt", "⌂", "Jedinstvena geometrija, etaže, orijentacija i BuildingModel."),
    EngineeringModule("architecture", "Architecture", "▦", "Usvojena LAT-ARCH-3D-001 arhitektura: model, engineering, mjerenja, validacija i visualization."),
    EngineeringModule("draft", "Tlocrt", "□", "Prostorije, zidovi, vrata, prozori i live dimensioning."),
    EngineeringModule("air", "Zrak", "↝", "Airflow Through Space: dovod, odsis, uzgon i zona čovjeka."),
    EngineeringModule("heat", "Grijanje", "♨", "Podno, radijatorsko, zidno, stropno, zračno i kombinirano."),
    EngineeringModule("cool", "Hlađenje", "❄", "Pasivno i aktivno hlađenje svježeg zraka i prostora."),
    EngineeringModule("water", "Voda", "≈", "Vodovod, cirkulacija, padovi, otpori i servisni pristup."),
    EngineeringModule("drain", "Odvodi", "⇩", "Odvodnja, nagibi, sifoni, revizije i hidraulički gubici."),
    EngineeringModule("electric", "Struja", "⚡", "Rasvjeta, utičnice, opterećenja, razvod i rezerva."),
    EngineeringModule("solar", "Solar", "☀", "Orijentacija krova, sjene, PV prinos i energija."),
    EngineeringModule("structure", "Statika", "⌂", "Masa, stalna i korisna opterećenja, snijeg i vjetar."),
    EngineeringModule("light", "Svjetlo", "◉", "Dnevno svjetlo prema prozorima, orijentaciji i dubini prostora."),
    EngineeringModule("materials", "Materijali", "▤", "Materijalna svojstva, masa, toplina, akustika i količine."),
    EngineeringModule("quantities", "Količine", "#", "Automatski obračun materijala i instalacija iz modela."),
    EngineeringModule("energy", "Energetika", "◇", "Toplinski gubici, dobici, ventilacija i godišnja energija."),
    EngineeringModule("acoustics", "Akustika", "))", "Buka, brzina zraka, ventilatori i prijenos zvuka."),
    EngineeringModule("service", "Servis", "⚙", "Pristup, revizije, zamjena, održavanje i servisna garancija."),
    EngineeringModule("ai", "AI prijedlozi", "✦", "LATCES predlaže optimizacije; čovjek prihvata ili odbija."),
)


class BuildingEngineeringWorkspace(tk.Frame):
    """Single-window engineering workspace around the existing BuildingModel."""

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.active = tk.StringVar(master=self, value="model")
        self._build()
        self._show("model")

    def _build(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        top = ttk.Frame(self, padding=(14, 10))
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        top.columnconfigure(1, weight=1)
        ttk.Label(top, text="LATCES", font=("Segoe UI", 17, "bold")).grid(row=0, column=0, padx=(0, 14))
        ttk.Label(top, text="BUILDING ENGINEERING WORKSPACE", font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Label(top, text="● MODEL CONNECTED", foreground="#15803d").grid(row=0, column=2, padx=(12, 0))

        side = ttk.Frame(self, padding=(10, 4, 8, 10))
        side.grid(row=1, column=0, sticky="nsw")
        ttk.Label(side, text="MODEL", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        for module in ENGINEERING_MODULES[:3]:
            self._nav_button(side, module)
        ttk.Label(side, text="SISTEMI", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(14, 4))
        for module in ENGINEERING_MODULES[3:11]:
            self._nav_button(side, module)
        ttk.Label(side, text="ANALIZA", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(14, 4))
        for module in ENGINEERING_MODULES[11:]:
            self._nav_button(side, module)

        self.main = ttk.Frame(self, padding=(4, 4, 14, 10))
        self.main.grid(row=1, column=1, sticky="nsew")
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(1, weight=1)

    def _nav_button(self, parent: ttk.Frame, module: EngineeringModule) -> None:
        ttk.Button(parent, text=f"{module.icon}  {module.title}", width=22, command=lambda k=module.key: self._show(k)).pack(fill="x", pady=1)

    def _clear(self) -> None:
        for child in self.main.winfo_children():
            child.destroy()

    def _show(self, key: str) -> None:
        self.active.set(key)
        self._clear()
        if key == "model":
            self._model()
        elif key == "architecture":
            self._architecture()
        elif key == "draft":
            self._drafting()
        elif key == "air":
            self._airflow()
        elif key in {"heat", "cool", "water", "drain", "electric", "solar", "structure"}:
            self._system(key)
        else:
            self._analysis(key)

    def _architecture(self) -> None:
        view = EngineeringArchitectureView(self.main)
        view.grid(row=0, column=0, rowspan=4, sticky="nsew")

    def _header(self, title: str, subtitle: str) -> None:
        ttk.Label(self.main, text=title, font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(self.main, text=subtitle, foreground="#64748b").grid(row=0, column=0, sticky="e")

    def _cards(self, values: list[tuple[str, str, str]]) -> None:
        frame = ttk.Frame(self.main)
        frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        for i, (title, value, note) in enumerate(values):
            frame.columnconfigure(i, weight=1)
            box = ttk.LabelFrame(frame, text=title, padding=10)
            box.grid(row=0, column=i, sticky="ew", padx=(0, 8))
            ttk.Label(box, text=value, font=("Segoe UI", 15, "bold")).pack(anchor="w")
            ttk.Label(box, text=note, foreground="#64748b", wraplength=180).pack(anchor="w", pady=(4, 0))

    def _model(self) -> None:
        self._header("Objekt", "jedan BuildingModel za sve proračune")
        body = ttk.Frame(self.main)
        body.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        box = ttk.LabelFrame(body, text="Geometrijska pravila", padding=12)
        box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        rows = (
            ("PRIZEMLJE", "10 × 10 × 2.80 m"),
            ("ETAŽA 1", "10 × 8 × 2.80 m"),
            ("ETAŽA 2", "10 × 8 × 2.80 m"),
            ("KROV", "10 × 10 m"),
            ("SJEVER", "↑"),
        )
        for row, (label, value) in enumerate(rows):
            ttk.Label(box, text=label, font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=5)
            ttk.Label(box, text=value).grid(row=row, column=1, sticky="w", padx=(35, 0), pady=5)
        info = ttk.LabelFrame(body, text="Jedinstveni lanac", padding=12)
        info.grid(row=0, column=1, sticky="nsew")
        ttk.Label(info, text="Tlocrt → BuildingModel → 3D → Presjek → Fizika → Prijedlog → Odluka", wraplength=330, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(info, text="Vrata/prozor su geometrijski otvor. Zid se automatski nastavlja iznad otvora do visine etaže.", wraplength=330).pack(anchor="w", pady=(14, 0))
        self._cards([("GEOMETRIJA", "CONNECTED", "jedan izvor istine"), ("3D", "LIVE", "iz iste geometrije"), ("AI", "ADVISOR", "čovjek odlučuje")])

    def _drafting(self) -> None:
        self._header("Tlocrt", "CAD/BIM način rada")
        toolbar = ttk.Frame(self.main)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(12, 8))
        for text in ("＋ Prostorija", "＋ Zid", "＋ Vrata", "＋ Prozor", "＋ Plenum"):
            ttk.Button(toolbar, text=text).pack(side="left", padx=(0, 6))
        canvas = tk.Canvas(self.main, background="#fafafa", highlightthickness=1, highlightbackground="#cbd5e1")
        canvas.grid(row=2, column=0, sticky="nsew")
        self.main.rowconfigure(2, weight=1)
        canvas.create_rectangle(110, 90, 650, 410, outline="#374151", width=4)
        canvas.create_line(110, 240, 650, 240, fill="#64748b", width=3)
        canvas.create_text(380, 150, text="DNEVNI BORAVAK", font=("Segoe UI", 11, "bold"))
        canvas.create_text(380, 330, text="SPAVAĆA SOBA", font=("Segoe UI", 11, "bold"))
        canvas.create_text(380, 62, text="10.00 m", fill="#b45309")
        canvas.create_text(690, 250, text="8.00 m", fill="#b45309", angle=90)
        canvas.create_line(300, 90, 360, 90, fill="#2563eb", width=7)
        canvas.create_text(330, 75, text="VRATA 0.90 × 2.10", fill="#1d4ed8", font=("Segoe UI", 9, "bold"))
        ttk.Label(self.main, text="Objekt prati miš → live dimenzije → snap → klik. Vrata/prozori prekidaju zid u 2D i 3D.", foreground="#475569").grid(row=3, column=0, sticky="w", pady=(7, 0))

    def _airflow(self) -> None:
        self._header("Airflow Through Space", "centralni modul toka zraka kroz prostor")
        content = ttk.Frame(self.main)
        content.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        content.rowconfigure(0, weight=1)
        canvas = tk.Canvas(content, background="#f8fafc", highlightthickness=1, highlightbackground="#cbd5e1")
        canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.main.rowconfigure(1, weight=1)
        x0, y0, x1, y1 = 100, 80, 650, 410
        canvas.create_rectangle(x0, y0, x1, y1, outline="#475569", width=3)
        canvas.create_line(x0, 230, x1, 230, fill="#94a3b8", dash=(5, 5))
        canvas.create_text(375, 145, text="ZONA BORAVKA 0.70–1.70 m", font=("Segoe UI", 11, "bold"))
        canvas.create_text(375, 215, text="minimalno primjetno strujanje", fill="#64748b")
        for yy in (155, 205, 275, 325):
            canvas.create_line(125, yy, 290, yy, arrow=tk.LAST, fill="#2563eb", width=2)
            canvas.create_line(350, yy, 610, yy, arrow=tk.LAST, fill="#16a34a", width=2)
        for xx in (180, 290, 400, 510):
            canvas.create_line(xx, 360, xx + 25, 290, arrow=tk.LAST, fill="#2563eb", width=2)
        canvas.create_text(155, 395, text="DOVODI", fill="#1d4ed8", font=("Segoe UI", 9, "bold"))
        canvas.create_text(575, 395, text="ODSIS", fill="#15803d", font=("Segoe UI", 9, "bold"))
        panel = ttk.LabelFrame(content, text="Live engineering state", padding=10)
        panel.grid(row=0, column=1, sticky="ns")
        values = (("Svježi zrak", "30–35 m³/h"), ("Ciljna brzina", "≤ 0.05 m/s"), ("Zona", "0.70–1.70 m"), ("Smjer", "dovod → prostor → odsis"), ("CO₂", "model / senzor"), ("VOC / HCHO", "model / senzor"), ("Uzgon", "AKTIVAN MODEL"))
        for label, value in values:
            ttk.Label(panel, text=label, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 0))
            ttk.Label(panel, text=value).pack(anchor="w", pady=(0, 5))
        self._cards([("IAQ", "MODEL", "CO₂ · VOC · HCHO · RH"), ("KOMFOR", "≤ 0.05 m/s", "brzina u zoni čovjeka"), ("ENERGIJA", "REKUPERACIJA", "prije aktivnog dogrijavanja/hlađenja")])

    def _system(self, key: str) -> None:
        module = next(m for m in ENGINEERING_MODULES if m.key == key)
        self._header(f"{module.icon}  {module.title}", module.description)
        ttk.Label(self.main, text="Ovaj ekran koristi isti BuildingModel. Nema drugog nacrta ni drugog izvora geometrije.", wraplength=700).grid(row=1, column=0, sticky="w", pady=(20, 10))
        self._cards([("GEOMETRIJA", "LINKED", "zidovi, prostorije, otvori"), ("PRORAČUN", "ENGINE", "scientific engine"), ("PRIJEDLOG", "AI", "predlaže, ne odlučuje")])

    def _analysis(self, key: str) -> None:
        module = next(m for m in ENGINEERING_MODULES if m.key == key)
        self._header(f"{module.icon}  {module.title}", module.description)
        body = ttk.LabelFrame(self.main, text="Engineering result", padding=14)
        body.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        self.main.rowconfigure(1, weight=1)
        ttk.Label(body, text="MODEL-DRIVEN", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(body, text="Ako nedostaje ulazni podatak, LATCES mora to jasno prijaviti umjesto da izmišlja vrijednost.", wraplength=650).pack(anchor="w", pady=(8, 18))
        ttk.Label(body, text="✓ geometrijska povezanost\n✓ materijalna svojstva\n✓ servisni pristup\n✓ AI prijedlog + ljudska odluka", font=("Segoe UI", 11)).pack(anchor="w")
        self._cards([("STATUS", "READY", "UI sloj"), ("TRACE", "BUILDING MODEL", "jedan izvor"), ("DECISION", "HUMAN", "prijedlog nije automatsko odobrenje")])


def launch() -> None:
    root = tk.Tk()
    root.title("LATCES — Building Engineering Workspace")
    root.geometry("1280x820")
    root.minsize(1050, 700)
    BuildingEngineeringWorkspace(root).pack(fill="both", expand=True)
    root.mainloop()


__all__ = ["BuildingEngineeringWorkspace", "ENGINEERING_MODULES", "launch"]
