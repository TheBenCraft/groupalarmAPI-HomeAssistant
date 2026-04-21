# GroupAlarm API Integration für Home Assistant

Diese Custom Integration ermöglicht es, persönliche Alarmierungen von [GroupAlarm](https://www.groupalarm.com) direkt in Home Assistant zu empfangen. Die Integration konzentriert sich auf den Endpunkt `/alarms/alarmed`, um nur die Einsätze anzuzeigen, für die du persönlich mitalarmiert wurdest.

## Features
- 🚀 **Echtzeit-nah:** Konfigurierbares Abfrageintervall (Standard: 30 Sekunden, Minimum: 15 Sekunden)
- 🚨 **Einsatz:** Zeigt das Alarmstichwort des aktuellen Einsatzes an
- 📬 **Alarmtext:** Zeigt die vollständige Einsatzmeldung an
- 🟢 **Status:** Zeigt ob ein Einsatz gerade aktiv ist (`Aktiv` / `Inaktiv`)
- 🙋 **Rückmeldung:** Zeigt deine persönliche Rückmeldung zum Alarm (`Zugesagt` / `Abgelehnt` / `Ausstehend`)
- 🛠 **Einfache Einrichtung:** Konfiguration direkt über die Home Assistant UI
- ⚙️ **Nachträgliche Neu-Konfiguration:** Alle Einstellungen können über „Neu konfigurieren" jederzeit geändert werden, ohne die Integration zu löschen

## Installation

### Über HACS (Empfohlen)
1. Öffne **HACS** in deinem Home Assistant.
2. Klicke oben rechts auf die drei Punkte und wähle **Benutzerdefinierte Repositories**.
3. Füge die URL dieses Repositories hinzu: `https://github.com/TheBenCraft/groupalarmAPI-HomeAssistant`
4. Wähle als Typ **Integration** und klicke auf **Hinzufügen**.
5. Suche nach „GroupAlarm API" und klicke auf **Herunterladen**.
6. Starte Home Assistant neu.

### Manuelle Installation
1. Kopiere den Ordner `custom_components/groupalarm_custom` in dein `/config/custom_components/` Verzeichnis.
2. Starte Home Assistant neu.

## Konfiguration
1. Gehe zu **Einstellungen** → **Geräte & Dienste**.
2. Klicke unten rechts auf **Integration hinzufügen**.
3. Suche nach **GroupAlarm API**.
4. Fülle die folgenden Felder aus:

| Feld | Beschreibung |
| :--- | :--- |
| **Personal Access Token** | Dein persönlicher API-Token aus dem GroupAlarm-Portal |
| **Organisation ID** | Die ID deiner Organisation |
| **User ID** | Deine persönliche User-ID (optional, für den Rückmeldungs-Sensor) |
| **Update-Intervall** | Wie oft die API abgefragt wird, in Sekunden (Minimum: 15) |
| **Alarm-Dauer** | Wie lange ein Alarm als „Aktiv" gilt, in Minuten |

### Einstellungen nachträglich ändern
- **„Neu konfigurieren"** (drei Punkte → Neu konfigurieren)

## Sensoren

Die Integration erstellt vier Sensoren unter dem Gerät **GroupAlarm**:

| Sensor | Beschreibung | Mögliche Werte |
| :--- | :--- | :--- |
| **Einsatz** | Alarmstichwort des aktuellen Einsatzes | Alarmstichwort oder `Kein Einsatz` |
| **Meldung** | Vollständiger Alarmtext | Meldungstext oder `Keine Meldung` |
| **Status** | Ob ein Einsatz gerade aktiv ist | `Aktiv`, `Inaktiv` |
| **Rückmeldung** | Deine persönliche Rückmeldung | `Zugesagt`, `Abgelehnt`, `Ausstehend`, `Kein Alarm`, `ID fehlt` |

> **Hinweis:** Von den Sensoren, Status und Rückmeldung werden im Automationseditor die möglichen Werte automatisch im Dropdown vorgeschlagen.

### Dashboard-Karte (Markdown)
```yaml
type: markdown
content: >
  ### 🚨 Aktueller Alarm

  **Einsatz:** {{ states('sensor.groupalarm_einsatz') }}

  **Meldung:** {{ states('sensor.groupalarm_meldung') }}

  **Status:** {{ states('sensor.groupalarm_status') }}

  **Rückmeldung:** {{ states('sensor.groupalarm_ruckmeldung') }}
```

## Wo finde ich Token und Org-ID?
- **Personal Access Token:** [GroupAlarm Portal](https://app.groupalarm.com) → Profil → API-Tokens
- **Organisation ID:** URL im GroupAlarm-Portal, z.B. `app.groupalarm.com/organization/12345` → `12345`
- **User ID:** GroupAlarm Portal → Profil → deine Benutzer-ID
