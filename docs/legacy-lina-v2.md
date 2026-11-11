---
title: Übernahme aus Lina v2 (Gemini)
---

# Übernahme aus Lina v2 (Gemini)

Quelle: `/Users/Agents/Lina JSI Gemini` (Git-Remote `d-selmanovic/Linav2-antigraphity`). Gemini 3.8 Live, FastAPI, FreeSWITCH, Airtable.

## Wird übernommen (überarbeitet)
- Persona und bosnischer Gesprächsstil (`prompts.py`): Ton, Spiegeln, Einwände, Robot-Frage, Closing
- Jobwissen → `docs/knowledge/job-angebot.md`
- Airtable-Felder und Telefon-Normalisierung (`airtable_service.py`) → `docs/airtable.md`
- Folgeprozesse (SMS, WhatsApp-Dokumente, Recruiter-Alert über Airtable-Automations) → bleiben außerhalb des Agents

## Wird ersetzt
- Gemini Live → GPT-Live 1 über LiveKit
- FastAPI und FreeSWITCH-WebSocket → LiveKit Agents, Telefonie später per LiveKit SIP
- Eigenes Recording, Langfuse und Logging → zuerst LiveKit Observability, Langfuse später optional
- Ein Prompt mit allen Fragen → Pre-Call-Fetch, nur fehlende Angaben

## Bewusst geändert
- Lina v2 fragt alles ab und schreibt am Ende per Upsert über die Telefonnummer. Neu: Fetch vorher, Patch auf eine feste Record-ID.
- Lina v2 ist eher inbound-artig aufgebaut (PBX verbindet). Neu: Outbound per Dispatch.
