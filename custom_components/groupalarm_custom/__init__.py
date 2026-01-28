import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setzt die Integration über einen Config Flow (UI) auf."""
    _LOGGER.info("Initialisiere GroupAlarm Custom Integration")

    # Registriert die Sensor-Plattform (sensor.py)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wird aufgerufen, wenn die Integration gelöscht oder deaktiviert wird."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return unload_ok
