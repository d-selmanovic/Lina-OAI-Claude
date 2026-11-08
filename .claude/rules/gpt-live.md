---
paths:
  - "src/**/*.py"
  - "prompts/**"
---

# GPT-Live-Regeln (OpenAI gpt-live-1)

Quelle: LiveKit-Doku `/agents/models/realtime/gpt-live`, Stand 05.11.2026. Vor Änderungen per `reading-livekit-docs` gegen die aktuelle Doku prüfen.

- **Zwei Instruktions-Sets:** Voice-Modell (Gesprächsführung) und Backend-Responses-Modell (`responses_options`, Reasoning und Tools). Ein Prompt für Turn-basierte Agents lässt sich nicht 1:1 übernehmen. Siehe OpenAI „Prompting GPT-Live“.
- **Kein wortgetreuer Text:** `session.say()` scheitert ohne TTS, und ein TTS-Hybrid ist nicht möglich. Pflichtformulierungen wie Begrüßung oder KI-Hinweis über Instruktionen erzwingen **und per Szenario prüfen**.
- **Handoffs** (Pozdrav / Daten / Kraj) starten bei GPT-Live eine neue Modell-Session. Verlauf mit `chat_ctx.copy(exclude_instructions=True)` mitgeben.
- Die Stimme lässt sich während der Session nicht wechseln. Der Kontext ist append-only, Kürzen ist nicht möglich.
- Barge-in steuert das Modell. Nach einer Unterbrechung kann es sich auf Ungehörtes beziehen.
- Keine Bilder, kein Video.
- Betrieb: LiveKit Inference (`openai/gpt-live-1`, LiveKit-Credentials, EU-Endpoint) oder OpenAI-Plugin (eigener Key). Entscheidung in ADR 0001.
