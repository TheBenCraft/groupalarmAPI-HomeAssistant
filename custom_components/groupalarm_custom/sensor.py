import logging
import async_timeout
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setzt die Sensoren anhand der Konfiguration auf."""
    token = config_entry.data.get("token")
    org_id = config_entry.data.get("org_id")
    
    # Intervall aus der config_flow abrufen, Standard 30 Sek
    scan_interval_seconds = config_entry.data.get("scan_interval", 30)
    
    # Das dynamische Scan-Intervall für diese Instanz festlegen
    scan_interval = timedelta(seconds=int(scan_interval_seconds))
    
    coordinator = GroupAlarmDataCoordinator(hass, token, org_id)
    
    # Entities hinzufügen
    entities = [
        GroupAlarmMainSensor(coordinator),
        GroupAlarmMessageSensor(coordinator),
        GroupAlarmStatusSensor(coordinator)
    ]
    
    async_add_entities(entities, True)

class GroupAlarmDataCoordinator:
    """Zentraler Datenabruf."""
    def __init__(self, hass, token, org_id):
        self.hass = hass
        self.token = token
        self.org_id = org_id
        self.data = {}

    async def update(self):
        url = "https://app.groupalarm.com/api/v1/alarms/alarmed"
        headers = {
            "Personal-Access-Token": self.token,
            "Organization-ID": self.org_id,
            "Content-Type": "application/json"
        }
        session = async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(10):
                response = await session.get(url, headers=headers)
                if response.status == 200:
                    self.data = await response.json()
                else:
                    _LOGGER.error("API Fehler: %s", response.status)
        except Exception as e:
            _LOGGER.error("Update fehlgeschlagen: %s", e)

class GroupAlarmMainSensor(SensorEntity):
    """Hauptsensor für den Einsatznamen."""
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "GroupAlarm Einsatz"
        self._attr_unique_id = f"ga_{coordinator.org_id}_main"
        self._attr_icon = "mdi:alarm-light"

    @property
    def state(self):
        alarms = self.coordinator.data.get("alarms", [])
        if isinstance(alarms, list) and len(alarms) > 0:
            return alarms[0].get("event", {}).get("name", "Kein Name")
        return "Kein Einsatz"

    @property
    def extra_state_attributes(self):
        alarms = self.coordinator.data.get("alarms", [])
        return {"alarms": alarms[:3]} if alarms else {}

    async def async_update(self):
        await self.coordinator.update()

class GroupAlarmMessageSensor(SensorEntity):
    """Sensor für die Alarmmeldung."""
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "GroupAlarm Meldung"
        self._attr_unique_id = f"ga_{coordinator.org_id}_message"
        self._attr_icon = "mdi:message-bulleted"

    @property
    def state(self):
        alarms = self.coordinator.data.get("alarms", [])
        if isinstance(alarms, list) and len(alarms) > 0:
            return alarms[0].get("message", "Keine Meldung")
        return "Keine Meldung"

class GroupAlarmStatusSensor(BinarySensorEntity):
    """Binary Sensor mit der 2-Stunden-Regel."""
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "GroupAlarm Status"
        self._attr_unique_id = f"ga_{coordinator.org_id}_status"
        self._attr_device_class = BinarySensorDeviceClass.SAFETY
        self._attr_icon = "mdi:fire-station"

    @property
    def is_on(self):
        alarms = self.coordinator.data.get("alarms", [])
        if not isinstance(alarms, list) or len(alarms) == 0:
            return False
        
        start_str = alarms[0].get("startDate")
        if not start_str:
            return False
            
        start_dt = dt_util.parse_datetime(start_str)
        if start_dt is None:
            return False
            
        diff = dt_util.now() - start_dt
        return diff.total_seconds() < 7200