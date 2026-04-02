import logging
import async_timeout
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    token = config_entry.data.get("token")
    org_id = config_entry.data.get("org_id")
    scan_sec = config_entry.data.get("scan_interval", 30)
    dur_min = config_entry.data.get("alarm_duration", 120)
    
    coordinator = GroupAlarmDataCoordinator(hass, token, org_id)
    
    entities = [
        GroupAlarmMainSensor(coordinator),
        GroupAlarmMessageSensor(coordinator),
        GroupAlarmStatusSensor(coordinator, dur_min)
    ]
    async_add_entities(entities, True)

class GroupAlarmDataCoordinator:
    def __init__(self, hass, token, org_id):
        self.hass, self.token, self.org_id, self.data = hass, token, org_id, {}

    async def update(self):
        url = "https://app.groupalarm.com/api/v1/alarms/alarmed"
        headers = {"Personal-Access-Token": self.token, "Organization-ID": self.org_id, "Content-Type": "application/json"}
        session = async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(10):
                response = await session.get(url, headers=headers)
                if response.status == 200:
                    self.data = await response.json()
        except Exception as e:
            _LOGGER.error("Update failed: %s", e)

class GroupAlarmMainSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name, self._attr_icon = "GroupAlarm Einsatz", "mdi:alarm-light"
        self._attr_unique_id = f"ga_{coordinator.org_id}_main"
    @property
    def state(self):
        alarms = self.coordinator.data.get("alarms", [])
        return alarms[0].get("event", {}).get("name", "Kein Name") if alarms else "Kein Einsatz"
    async def async_update(self): await self.coordinator.update()

class GroupAlarmMessageSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name, self._attr_icon = "GroupAlarm Meldung", "mdi:message-bulleted"
        self._attr_unique_id = f"ga_{coordinator.org_id}_message"
    @property
    def state(self):
        alarms = self.coordinator.data.get("alarms", [])
        return alarms[0].get("message", "Keine Meldung") if alarms else "Keine Meldung"

class GroupAlarmStatusSensor(BinarySensorEntity):
    def __init__(self, coordinator, dur_min):
        self.coordinator = coordinator
        self._dur_sec = dur_min * 60
        self._attr_name, self._attr_icon = "GroupAlarm Status", "mdi:fire-station"
        self._attr_device_class = BinarySensorDeviceClass.SAFETY
        self._attr_unique_id = f"ga_{coordinator.org_id}_status"
    @property
    def is_on(self):
        alarms = self.coordinator.data.get("alarms", [])
        if not alarms: return False
        start_dt = dt_util.parse_datetime(alarms[0].get("startDate", ""))
        if not start_dt: return False
        return (dt_util.now() - start_dt).total_seconds() < self._dur_sec
