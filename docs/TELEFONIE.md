---
title: "Telefonie: LiveKit → FusionPBX → TG400 → SIM"
---

# Telefonie: LiveKit → FusionPBX → TG400 → SIM

Stand 06.11.2026, erster erfolgreicher Testanruf. Keine Passwörter in dieser Datei.

## Weg eines Anrufs
```text
LiveKit Cloud (Lina, Agent livekit-oai-gig-casting)
  │  Outbound-Trunk ST_pN6ccnMf26NY „FusionPBX Outbound (Lina)“
  ▼
FusionPBX fusion.activi.io:5060 (Profil internal, UDP, Login als Nebenstelle 300)
  │  Ausgehende Route „TG400_Outbound“ (Reihenfolge 100)
  ▼
Gateway „TG400“ (ID 5e889af0-e082-488f-b96f-f247b88725cc, Profil internal, ohne Registrierung)
  ▼
Yeastar TG400 (Bihać, LAN 192.168.31.150, öffentlich 213.91.103.192) → SIM 1 m:tel → Handy
```
Der Angerufene sieht die Nummer der SIM 1 (m:tel).

## LiveKit-Trunk (Dashboard → Telephony → Trunks)
- address `fusion.activi.io:5060`, transport UDP, numbers `["300"]`, auth_username `300`
- from_host `fusion.activi.io` (FusionPBX ordnet den Anruf so der Domain zu)
- Passwort = Passwort von Nebenstelle 300 (nur im Dashboard, nirgends sonst)

## FusionPBX
- Nebenstelle **300**: wird vom TG400 (Anmeldung) und von LiveKit (Anruf mit Login) genutzt.
- Route **call_direction-outbound** (22): setzt nur `call_direction=outbound`, nicht ändern.
- Route **TG400_Outbound** (100): Muster `^(?:\+|00)?([1-9]\d{7,14})$`,
  bridge in der Tabellenansicht `sofia/gateway/TG400/00$1` (FusionPBX setzt intern die ID ein).
  Änderungen nur in der Tabellenansicht, der XML-Editor wird aus der Tabelle neu erzeugt.
- Nach Änderungen: SIP Status → Cache leeren.
- Zurück auf sipgate: bridge `sofia/gateway/sipgate-Trunk/$1`.

## TG400
- Trunk „fusion“: Register-Trunk zu fusion.activi.io, Benutzer 300, UDP 5060.
- Codecs nur a-law, u-law, GSM (kein G722).
- Firewall an, keine IP gesperrt. Nichts öffnen, was nicht nötig ist.

## Testanruf
`testanruf.json` (nicht im Repo, steht in .gitignore):
```json
{"sip_trunk_id": "ST_pN6ccnMf26NY", "sip_call_to": "+387…", "room_name": "lina-test-…",
 "participant_identity": "kandidat", "wait_until_answered": true}
```
```bash
lk sip participant create testanruf.json && \
lk dispatch create --room <room_name> --agent-name livekit-oai-gig-casting \
  --metadata '{"record_id":"rec17GODhyD0Lkgzp"}'
```

## Fehlerbilder
- 480 und `last_arg` mit Gateway `5c24281b…`: Anruf ging an sipgate (Route falsch).
- 484 Address Incomplete: Nummer passt nicht, `last_arg` im FusionPBX-Anrufprotokoll prüfen.
- Kein Eintrag in TG400 → Call Logs: Anruf erreicht den TG400 nicht.

## Offen
- Feste öffentliche IP des TG400-Standorts klären (Gateway nutzt 213.91.103.192).
- Lina wählt noch nicht selbst: Anruf wird per `lk sip participant create` gestartet,
  Lina kommt nach dem Abheben dazu (ca. 4–5 s Pause).
- Eigene Nebenstelle für LiveKit statt 300 (Trennung von TG400).
