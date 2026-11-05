"""Langfuse-Tracing über OpenTelemetry (LiveKit-Doku: /testing/observability/tracing).

Aktiv nur, wenn LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY und LANGFUSE_BASE_URL gesetzt sind.
Ohne Keys läuft Lina normal weiter (kein Absturz).

Datenschutz: Standardmäßig gehen KEINE Gesprächsinhalte an Langfuse (`allow_pii=False`):
nur Dauer, Modelle, Tokens, Tool-Namen, Fehler-Typen. Mit LANGFUSE_INHALTE=1 werden auch
Transkripte, Tool-Argumente und Instruktionen übertragen (= Personendaten der Kandidaten).
"""

from __future__ import annotations

import base64
import logging
import os

from opentelemetry.util.types import AttributeValue

logger = logging.getLogger("lina.telemetrie")


def setup_langfuse(metadata: dict[str, AttributeValue] | None = None):
    """Gibt den TracerProvider zurück oder None, wenn Langfuse nicht konfiguriert ist."""
    pk = os.environ.get("LANGFUSE_PUBLIC_KEY")
    sk = os.environ.get("LANGFUSE_SECRET_KEY")
    base = os.environ.get("LANGFUSE_BASE_URL")
    if not (pk and sk and base):
        logger.info("Langfuse nicht konfiguriert – Tracing aus")
        return None

    from livekit.agents.telemetry import set_tracer_provider
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    auth = base64.b64encode(f"{pk}:{sk}".encode()).decode()
    exporter = OTLPSpanExporter(
        endpoint=f"{base.rstrip('/')}/api/public/otel/v1/traces",
        headers={"Authorization": f"Basic {auth}", "x-langfuse-ingestion-version": "4"},
    )
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    inhalte = os.environ.get("LANGFUSE_INHALTE", "0") == "1"
    set_tracer_provider(provider, metadata=metadata, allow_pii=inhalte)
    logger.info("Langfuse-Tracing aktiv (Inhalte: %s)", "ja" if inhalte else "nein")
    return provider
