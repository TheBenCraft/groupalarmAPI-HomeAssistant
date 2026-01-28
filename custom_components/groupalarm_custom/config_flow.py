import voluptuous as vol
from homeassistant import config_entries
import logging

DOMAIN = "groupalarm_custom"
_LOGGER = logging.getLogger(__name__)

class GroupAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Behandelt das Setup-Fenster."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Erstellt den Eintrag in der UI
            return self.async_create_entry(title="GroupAlarm", data=user_input)

        # Das Formular, das angezeigt wird
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("token"): str,
                vol.Required("org_id"): str,
            }),
        )