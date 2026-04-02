import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import logging

DOMAIN = "groupalarm_custom"

class GroupAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(user_input["token"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"GroupAlarm ({user_input['org_id']})", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("token"): str,
                vol.Required("org_id"): str,
                vol.Optional("scan_interval", default=30): vol.All(vol.Coerce(int), vol.Range(min=15)),
                vol.Optional("alarm_duration", default=120): vol.All(vol.Coerce(int), vol.Range(min=1)),
            }),
        )
