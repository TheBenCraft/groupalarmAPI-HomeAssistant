import asyncio
import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup der GroupAlarm Sensoren."""
    token = config_entry.data.get("token")
    org_id = config_entry.data.get("org_id")
    scan_interval = config_entry.options.get(
        "scan_interval", config_entry.data.get("scan_interval", 30)
    )
    dur_min = config_entry.options.get(
        "alarm_duration", config_entry.data.get("alarm_duration", 120)
    )
    user_id = config_entry.options.get(
        "user_id", config_entry.data.get("user_id", 0)
    )

    coordinator = GroupAlarmDataCoordinator(hass, token, org_id, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    device_info = DeviceInfo(
        identifiers={(DOMAIN, org_id)},
        name="GroupAlarm",
        manufacturer="TheBenCraft",
        model="GroupAlarm API Integration",
        configuration_url="https://app.groupalarm.com/",
    )

    entities = [
        GroupAlarmMainSensor(coordinator, device_info),
        GroupAlarmMessageSensor(coordinator, device_info),
        GroupAlarmStatusSensor(coordinator, dur_min, device_info),
        GroupAlarmFeedbackSensor(coordinator, user_id, device_info),
    ]
    async_add_entities(entities)


class GroupAlarmDataCoordinator(DataUpdateCoordinator):
    """Koordiniert den Datenabruf von der GroupAlarm API."""

    def __init__(self, hass, token, org_id, scan_interval):
        super().__init__(
            hass,
            _LOGGER,
            name="GroupAlarm",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.token = token
        self.org_id = org_id

    async def _async_update_data(self):
        """Ruft aktuelle Alarmdaten von der API ab."""
        url = "https://app.groupalarm.com/api/v1/alarms/alarmed"
        headers = {
            "Personal-Access-Token": self.token,
            "Organization-ID": self.org_id,
            "Content-Type": "application/json",
        }
        session = async_get_clientsession(self.hass)
        try:
            async with asyncio.timeout(10):
                response = await session.get(url, headers=headers)
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            raise UpdateFailed(f"GroupAlarm API-Fehler: {e}") from e


class GroupAlarmBaseSensor(CoordinatorEntity, SensorEntity):
    """Basisklasse für alle GroupAlarm Sensoren."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GroupAlarmDataCoordinator, device_info: DeviceInfo):
        super().__init__(coordinator)
        self._attr_device_info = device_info


class GroupAlarmMainSensor(GroupAlarmBaseSensor):
    """Zeigt den Namen des aktuellen Einsatzes."""

    def __init__(self, coordinator, device_info):
        super().__init__(coordinator, device_info)
        self._attr_name = "Einsatz"
        self._attr_unique_id = f"ga_{coordinator.org_id}_main"

    @property
    def icon(self):
        return "mdi:alarm-light"

    @property
    def native_value(self):
        alarms = self.coordinator.data.get("alarms", []) if self.coordinator.data else []
        return alarms[0].get("event", {}).get("name", "Kein Einsatz") if alarms else "Kein Einsatz"

    @property
    def extra_state_attributes(self):
        """Gibt den kompletten API-Output als Attribut zurück."""
        return {"api_response": self.coordinator.data if self.coordinator.data else {}}


class GroupAlarmMessageSensor(GroupAlarmBaseSensor):
    """Zeigt die Meldung des aktuellen Alarms."""

    def __init__(self, coordinator, device_info):
        super().__init__(coordinator, device_info)
        self._attr_name = "Meldung"
        self._attr_unique_id = f"ga_{coordinator.org_id}_message"

    @property
    def icon(self):
        return "mdi:message-bulleted"

    @property
    def native_value(self):
        alarms = self.coordinator.data.get("alarms", []) if self.coordinator.data else []
        return alarms[0].get("message", "Keine Meldung") if alarms else "Keine Meldung"


class GroupAlarmFeedbackSensor(GroupAlarmBaseSensor):
    """Zeigt die eigene Rückmeldung zum aktuellen Alarm."""

    def __init__(self, coordinator, user_id, device_info):
        super().__init__(coordinator, device_info)
        self.user_id = str(user_id)
        self._attr_name = "Rückmeldung"
        self._attr_unique_id = f"ga_{coordinator.org_id}_feedback"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["Zugesagt", "Abgelehnt", "Ausstehend", "Kein Alarm", "ID fehlt"]

    @property
    def icon(self):
        return "mdi:account-question"

    @property
    def capability_attributes(self):
        """Gibt die ENUM-Optionen explizit als Capability zurück."""
        attrs = super().capability_attributes or {}
        attrs = dict(attrs)
        attrs["options"] = self._attr_options
        return attrs

    @property
    def native_value(self):
        if not self.user_id or self.user_id == "0":
            return "ID fehlt"

        alarms = self.coordinator.data.get("alarms", []) if self.coordinator.data else []
        if not alarms:
            return "Kein Alarm"

        for r in alarms[0].get("feedback", []):
            if str(r.get("userID")) == self.user_id:
                state = r.get("state", "")
                if state == "WAITING":
                    return "Ausstehend"
                if r.get("feedback") is True:
                    return "Zugesagt"
                if r.get("feedback") is False:
                    return "Abgelehnt"

        return "Ausstehend"


class GroupAlarmStatusSensor(GroupAlarmBaseSensor):
    """Zeigt ob ein Alarm gerade aktiv ist."""

    def __init__(self, coordinator, dur_min, device_info):
        super().__init__(coordinator, device_info)
        self._dur_sec = dur_min * 60
        self._attr_name = "Status"
        self._attr_unique_id = f"ga_{coordinator.org_id}_status"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["Aktiv", "Inaktiv"]

    @property
    def icon(self):
        return "mdi:fire-station"

    @property
    def capability_attributes(self):
        """Gibt die ENUM-Optionen explizit als Capability zurück."""
        attrs = super().capability_attributes or {}
        attrs = dict(attrs)
        attrs["options"] = self._attr_options
        return attrs

    @property
    def native_value(self):
        alarms = self.coordinator.data.get("alarms", []) if self.coordinator.data else []
        if not alarms:
            return "Inaktiv"

        start_dt = dt_util.parse_datetime(alarms[0].get("startDate", ""))
        if not start_dt:
            return "Inaktiv"

        elapsed = (dt_util.now() - start_dt).total_seconds()
        return "Aktiv" if elapsed < self._dur_sec else "Inaktiv"
