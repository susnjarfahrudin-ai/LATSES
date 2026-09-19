"""Read-only ministerial oversight workspace for LAT-CES."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lat_ces.agriculture.ministerial import build_official_snapshot
from lat_ces.scientific.core.governance import AssuranceEngine, GovernanceDecision, ScientificArtifact
from lat_ces.scientific.evidence_state import EvidenceState


class MinisterWorkspaceApp(tk.Tk):
    """Read-only oversight dashboard for ministerial review."""

    def __init__(
        self,
        *,
        artifacts: tuple[ScientificArtifact, ...] = (),
        decisions: tuple[GovernanceDecision, ...] = (),
    ) -> None:
        super().__init__()
        self.title("LAT-CES — Ministarski pregled")
        self.geometry("1280x780")
        self.minsize(980, 620)
        self._artifacts = tuple(artifacts)
        self._decisions = tuple(decisions)
        self._agriculture = build_official_snapshot()
        self._build()

    def _build(self) -> None:
        header = ttk.Frame(self, padding=18)
        header.pack(fill="x")
        ttk.Label(header, text="LAT-CES — MINISTARSKI PREGLED", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            header,
            text="Dokazi, odluke i sektorska evolucija — read-only pregled.",
        ).pack(anchor="w", pady=(4, 0))

        summary = ttk.Frame(self, padding=(18, 4, 18, 10))
        summary.pack(fill="x")
        self._summary = tk.StringVar()
        ttk.Label(summary, textvariable=self._summary, font=("Segoe UI", 11, "bold")).pack(anchor="w")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        evidence_tab = ttk.Frame(notebook, padding=10)
        decisions_tab = ttk.Frame(notebook, padding=10)
        agriculture_tab = ttk.Frame(notebook, padding=10)
        principles_tab = ttk.Frame(notebook, padding=10)
        notebook.add(evidence_tab, text="Dokazi")
        notebook.add(decisions_tab, text="Odluke")
        notebook.add(agriculture_tab, text="Poljoprivreda — evolucija")
        notebook.add(principles_tab, text="Granice sistema")

        self._build_evidence(evidence_tab)
        self._build_decisions(decisions_tab)
        self._build_agriculture(agriculture_tab)
        self._build_principles(principles_tab)
        self._refresh_summary()

    def _build_evidence(self, tab: ttk.Frame) -> None:
        columns = ("id", "lifecycle", "evidence", "assurance", "provenance")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        headings = {"id": "Artefakt", "lifecycle": "Lifecycle", "evidence": "Dokaz", "assurance": "Assurance", "provenance": "Provenance"}
        widths = {"id": 280, "lifecycle": 110, "evidence": 110, "assurance": 110, "provenance": 260}
        for key in columns:
            tree.heading(key, text=headings[key])
            tree.column(key, width=widths[key], anchor="w")
        tree.pack(fill="both", expand=True)
        for artifact in self._artifacts:
            assurance = AssuranceEngine().assess(artifact)
            tree.insert("", "end", values=(artifact.artifact_id, artifact.state.value, artifact.evidence_state.value, assurance.level, ", ".join(artifact.provenance)))

    def _build_decisions(self, tab: ttk.Frame) -> None:
        columns = ("id", "authority", "decision", "evidence")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        for key, title, width in (("id", "ID", 270), ("authority", "Autoritet", 170), ("decision", "Odluka", 300), ("evidence", "Dokaz", 320)):
            tree.heading(key, text=title)
            tree.column(key, width=width, anchor="w")
        tree.pack(fill="both", expand=True)
        for item in self._decisions:
            tree.insert("", "end", values=(item.decision_id, item.authority, item.decision, ", ".join(item.evidence)))

    def _build_agriculture(self, tab: ttk.Frame) -> None:
        ttk.Label(
            tab,
            text="POLJOPRIVREDA — EVOLUCIJA | BiH · Evropa · Svijet",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 8))
        ttk.Label(
            tab,
            text="Istorijski trendovi i outlook su odvojeni. Svaka vrijednost nosi period, izvor i jedinicu.",
        ).pack(anchor="w", pady=(0, 8))

        notebook = ttk.Notebook(tab)
        notebook.pack(fill="both", expand=True)

        for scope in ("BiH", "EU", "Svijet"):
            page = ttk.Frame(notebook, padding=8)
            notebook.add(page, text=scope)
            columns = ("indicator", "period", "evolution", "source", "interpretation")
            tree = ttk.Treeview(page, columns=columns, show="headings")
            for key, title, width in (
                ("indicator", "Indikator", 250),
                ("period", "Period", 150),
                ("evolution", "Promjena / stanje", 180),
                ("source", "Izvor", 180),
                ("interpretation", "Napomena", 430),
            ):
                tree.heading(key, text=title)
                tree.column(key, width=width, anchor="w")
            tree.pack(fill="both", expand=True)
            for item in self._agriculture.evolution_for(scope):
                tree.insert("", "end", values=(item.indicator, item.period, item.evolution, item.source, item.interpretation))

    def _build_principles(self, tab: ttk.Frame) -> None:
        text = tk.Text(tab, wrap="word", height=18)
        text.pack(fill="both", expand=True)
        lines = (
            "MINISTARSKI PREGLED — GRANICE",
            "",
            "• Aplikacija je read-only pregled.",
            "• ScientificArtifact ostaje canonical izvor znanstvenog rezultata.",
            "• EvidenceState je odvojen od lifecycle statusa.",
            "• Novi revision vraća evidence stanje na UNKNOWN dok se dokaz ponovo ne uspostavi.",
            "• Governance odluke moraju imati autoritet, obrazloženje i dokaz.",
            "• Poljoprivredni podaci su source-labelled; BiH, EU i Svijet se ne spajaju u jednu metodologiju.",
            "• RCI-AD nije decision owner ovog interfejsa.",
            "• Rate limiter nije pod kontrolom ovog interfejsa.",
            "• Ovaj interfejs ne mijenja BuildingModel niti sigurnosne pragove.",
        )
        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")

    def _refresh_summary(self) -> None:
        measured = sum(a.evidence_state is EvidenceState.MEASURED for a in self._artifacts)
        verified = sum(a.evidence_state is EvidenceState.VERIFIED for a in self._artifacts)
        unknown = sum(a.evidence_state is EvidenceState.UNKNOWN for a in self._artifacts)
        self._summary.set(
            f"Artefakti: {len(self._artifacts)}  |  MEASURED: {measured}  |  VERIFIED: {verified}  |  UNKNOWN: {unknown}  |  Odluke: {len(self._decisions)}"
        )


def main() -> None:
    MinisterWorkspaceApp().mainloop()


__all__ = ["MinisterWorkspaceApp", "main"]
