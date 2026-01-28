import logging
import async_timeout
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Richtet den Sensor basierend auf den UI-Eingaben ein."""
    token = config_entry.data.get("token")
    org_id = config_entry.data.get("org_id")
    async_add_entities([GroupAlarmSensor(token, org_id)], True)

class GroupAlarmSensor(SensorEntity):
    def __init__(self, token, org_id):
        self._token = token
        self._org_id = org_id
        self._attr_name = "GroupAlarm Einsatz"
        self._attr_unique_id = f"ga_{org_id}_main"
        self._state = "Initialisierung..."
        self._attributes = {}

    @property
    def state(self): return self._state

    @property
    def extra_state_attributes(self): return self._attributes

    async def async_update(self):
        """Holt Daten von der API (Asynchron)."""
        url = "https://app.groupalarm.com/api/v1/alarms/alarmed"
        headers = {
            "Personal-Access-Token": self._token,
            "Organization-ID": self._org_id,
            "Content-Type": "application/json"
        }
        
        session = async_get_clientsession(self.hass)
        try:
            with async_timeout.timeout(10):
                response = await session.get(url, headers=headers)
                data = await response.json()
                alarms = data.get("alarms", [])

                if alarms:
                    latest = alarms[0]
                    self._state = f"{latest.get('eventName')} - {latest.get('createdAt')}"
                    self._attributes = {
                        "message": latest.get("message"),
                        "alarms": alarms
                    }
                else:
                    self._state = "Kein Einsatz"
                    self._attributes = {"alarms": []}
        except Exception as e:
            _LOGGER.error("Fehler bei GroupAlarm Abfrage: %s", e)
            self._state = "Fehler"
