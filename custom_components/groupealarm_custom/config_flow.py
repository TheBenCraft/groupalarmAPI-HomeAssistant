import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "groupalarm_custom"

class GroupAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Prozess für die Einrichtung in der Benutzeroberfläche."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="GroupAlarm Account", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("token"): str,
                vol.Required("org_id"): str,
            }),
        )
