# 📟 GroupAlarm Personal Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

Diese Integration bringt deine persönlichen **GroupAlarm-Einsätze** direkt in dein Home Assistant Dashboard.

### Warum diese Integration?
Im Gegensatz zu Standard-Abfragen filtert diese Integration automatisch alle Alarme heraus, die dich nicht betreffen. Du siehst nur das, was für **dich** relevant ist.

### ✨ Highlights
* **Echtzeit-Status:** Sofortige Anzeige von Einsatzname und Zeitstempel.
* **Vollständige Details:** Der gesamte Alarmtext wird in den Attributen gespeichert.
* **Einfacher Setup:** Keine YAML-Kenntnisse erforderlich – gib Token und ID einfach in der Benutzeroberfläche ein.
* **Smart History:** Der letzte Alarmtext bleibt sichtbar, bis eine neue Meldung eingeht.

### 🛠 Installation & Einrichtung
1. Füge dieses Repository in HACS als **Custom Repository** hinzu.
2. Lade die Integration herunter und starte Home Assistant neu.
3. Gehe zu **Einstellungen > Geräte & Dienste** und füge "GroupAlarm Personal" hinzu.

---
*Hinweis: Erfordert einen gültigen Personal-Access-Token von GroupAlarm.*
