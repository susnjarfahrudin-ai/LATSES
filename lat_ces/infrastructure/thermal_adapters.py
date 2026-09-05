"""External adapters for thermal validation workflow actions.

These adapters are infrastructure concerns. They consume application-level
WorkflowAction objects and do not participate in scientific validation.
"""
from __future__ import annotations

import html
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from urllib.parse import quote

from lat_ces.application.workflow_service import WorkflowAction, WorkflowAdapter


class EmailWorkflowAdapter(WorkflowAdapter):
    """SMTP adapter for INPUT_BLOCKER notifications."""

    def __init__(
        self,
        *,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        sender: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.smtp_host = smtp_host or os.getenv("LATCES_SMTP_HOST")
        self.smtp_port = smtp_port or int(os.getenv("LATCES_SMTP_PORT", "587"))
        self.sender = sender or os.getenv("LATCES_SMTP_SENDER")
        self.password = password or os.getenv("LATCES_SMTP_PASSWORD")

    def dispatch(self, action: WorkflowAction) -> None:
        if action.kind != "INPUT_BLOCKER":
            return
        if not self.smtp_host or not self.sender or not self.password:
            raise RuntimeError("SMTP adapter is not configured")

        recipient = os.getenv(
            f"LATCES_ROLE_EMAIL_{action.target.upper().replace(' ', '_').replace('/', '_')}"
        )
        if not recipient:
            raise RuntimeError(f"No email mapping configured for role: {action.target}")

        p = action.payload
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[LATCES INPUT_REQUIRED] Missing {p['field']}"
        msg["From"] = self.sender
        msg["To"] = recipient
        body = "".join(
            [
                "<html><body>",
                "<h3>LATCES calculation blocked</h3>",
                f"<p>Status: <b>{html.escape(str(p['status']))}</b></p>",
                f"<p>Project: <b>{html.escape(str(p['project_id']))}</b></p>",
                f"<p>Zone: <b>{html.escape(str(p['zone_id']))}</b></p>",
                f"<p>Element: <b>{html.escape(str(p['element_id']))}</b></p>",
                f"<p>Missing/invalid field: <b>{html.escape(str(p['field']))}</b></p>",
                f"<p>Expected unit: <b>{html.escape(str(p['expected_unit']))}</b></p>",
                f"<p>Hint: {html.escape(str(p['hint']))}</p>",
                "<p>No value was guessed by LATCES.</p>",
                "</body></html>",
            ]
        )
        msg.attach(MIMEText(body, "html"))
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender, self.password)
            server.sendmail(self.sender, [recipient], msg.as_string())


class DeepLinkAdapter:
    """Build stable application URLs for blocked inputs."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def url_for(self, action: WorkflowAction) -> str:
        if action.kind != "INPUT_BLOCKER":
            raise ValueError("deep links are defined for INPUT_BLOCKER actions")
        p = action.payload
        return (
            f"{self.base_url}/projects/{quote(str(p['project_id']))}/zones/"
            f"{quote(str(p['zone_id']))}/{quote(str(p['category']))}"
            f"?focus={quote(str(p['element_id']))}&input={quote(str(p['field']))}"
        )


__all__ = ["EmailWorkflowAdapter", "DeepLinkAdapter"]
