# GroupAlarm Personal-API Integration für Home Assistant

Diese Custom Integration ermöglicht es, persönliche Alarmierungen von [GroupAlarm](https://www.groupalarm.com) direkt in Home Assistant zu empfangen. Im Gegensatz zu allgemeinen Abfragen konzentriert sich diese Integration auf den Endpunkt `/alarms/alarmed`, um nur die Einsätze anzuzeigen, für die du persönlich mitalarmiert wurdest.

## Features
- 🚀 **Echtzeit-nah:** Standard-Abfrageintervall von 30 Sekunden.
- 📬 **Alarmtext:** Extrahiert die Einsatzmeldung direkt aus den Sensor-Attributen.
- 📅 **Status-Anzeige:** Einsatzname im Hauptstatus.
- 🛠 **Einfache Einrichtung:** Konfiguration direkt über die Home Assistant Benutzeroberfläche (Config Flow).
- 💾 **Persistent:** Der letzte Alarmtext bleibt erhalten, auch wenn aktuell kein Einsatz aktiv ist.

## Installation

### Über HACS (Empfohlen)
1. Öffne **HACS** in deinem Home Assistant.
2. Klicke oben rechts auf die drei Punkte und wähle **Benutzerdefinierte Repositories**.
3. Füge die URL dieses Repositories hinzu: `https://github.com/TheBenCraft/groupalarmAPI-HomeAssistant.git`
4. Wähle als Typ **Integration** und klicke auf **Hinzufügen**.
5. Suche nach "GroupAlarm Personal" und klicke auf **Herunterladen**.
6. Starte Home Assistant neu.

### Manuelle Installation
1. Kopiere den Ordner `custom_components/groupalarm_custom` in dein `/config/custom_components/` Verzeichnis.
2. Starte Home Assistant neu.

## Konfiguration
1. Gehe zu **Einstellungen** -> **Geräte & Dienste**.
2. Klicke unten rechts auf **Integration hinzufügen**.
3. Suche nach **GroupAlarm Personal**.
4. Gib deinen **Personal-Access-Token** und deine **Organization-ID** ein.

## Sensoren & Attribute
Die Integration erstellt eine Entität: `sensor.groupalarm_einsatz`.

| Attribut | Beschreibung |
| :--- | :--- |
| `State` | Name des Events + Zeitstempel |
| `message` | Der vollständige Alarmtext/Einsatzmeldung |
| `alarms` | Die komplette JSON-Antwort der API für fortgeschrittene Automatisierungen |

## Beispiel für eine Dashboard-Karte (Markdown)
Um den Alarmtext schön anzuzeigen, kannst du diese Karte nutzen:

```yaml
type: markdown
content: >
  ### 🚨 Letzter Alarm
  **Einsatz:** {{ states('sensor.groupalarm_einsatz') }}
  
  **Meldung:**
  {{ states('sensor.groupalarm_meldung') }}
