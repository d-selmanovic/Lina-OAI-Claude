---
title: Deploy auf LiveKit Cloud
---

# Deploy auf LiveKit Cloud

Projekt `lina-oai` (`p_40xj9wk3r8d`), Agent-Name `livekit-oai-gig-casting`, Region **eu-central** (EU).

## 1. Secrets-Datei anlegen (nicht committen)
`LIVEKIT_URL`, `LIVEKIT_API_KEY` und `LIVEKIT_API_SECRET` setzt LiveKit Cloud **selbst**. Sie dürfen
nicht als Secret mitgegeben werden. Deshalb eine eigene Datei `.env.cloud` anlegen
(sie ist über `.env.*` in `.gitignore` ausgeschlossen):

```text
AIRTABLE_API_KEY=pat...
AIRTABLE_BASE_ID=appz3VFomHaWhuILV
AIRTABLE_TABLE=tbl7WHRtBkRX7tGxt
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
LANGFUSE_INHALTE=1
# NUR für die Testphase: Agent Console ohne Metadaten → Test-Kandidat K-0196.
# Vor echten Anrufen ENTFERNEN (sonst landen Tests ohne Kandidat bei K-0196).
LINA_TEST_RECORD_ID=rec17GODhyD0Lkgzp
```

## 2. Erstes Deploy
```bash
lk agent create --region eu-central --secrets-file .env.cloud
```
Legt `livekit.toml` mit der Agent-ID an (die Datei committen, sie enthält keine Secrets).

## 3. Weitere Versionen
```bash
lk agent deploy
lk agent status
lk agent logs
```
Secrets ändern: `lk agent update-secrets --secrets-file .env.cloud` (Befehl vorher mit
`lk agent --help` prüfen).

## 4. Testen in der Cloud
- **Agent Console** im LiveKit-Dashboard → Agent `livekit-oai-gig-casting` → sprechen. Dort hörst
  du Lina und siehst Transkript, Tool-Aufrufe und Zeiten.
- **Audio-Simulationen gegen den deployten Agent:**
  ```bash
  lk agent simulate audio --agent-name livekit-oai-gig-casting --scenarios scenarios.yaml
  ```
- **Langfuse:** Traces unter dem Raumnamen (`langfuse.session.id`).

## Rollback
Im Build-Plan gibt es kein Instant-Rollback. Notfalls älteren Commit auschecken und `lk agent deploy`.
