import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class GroupAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Behandelt die Ersteinrichtung und Duplikat-Prüfung."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input["token"])
            self._abort_if_unique_id_configured()

            # user_id als int speichern, leer → 0
            user_input["user_id"] = int(user_input["user_id"]) if user_input.get("user_id") else 0

            return self.async_create_entry(
                title=f"GroupAlarm ({user_input['org_id']})",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("token"): str,
                    vol.Required("org_id"): str,
                    vol.Optional("user_id"): str,
                    vol.Optional("scan_interval", default=30): vol.All(
                        vol.Coerce(int), vol.Range(min=15)
                    ),
                    vol.Optional("alarm_duration", default=120): vol.All(
                        vol.Coerce(int), vol.Range(min=1)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        """Ermöglicht das Ändern aller Felder über 'Neu konfigurieren'."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input["token"])
            self._abort_if_unique_id_configured(updates=user_input)

            user_input["user_id"] = int(user_input["user_id"]) if user_input.get("user_id") else 0

            return self.async_update_reload_and_abort(
                entry,
                title=f"GroupAlarm ({user_input['org_id']})",
                data=user_input,
            )

        # Gespeicherte user_id: 0 als leer darstellen
        saved_uid = entry.data.get("user_id", 0)
        uid_default = str(saved_uid) if saved_uid else ""

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required("token", default=entry.data.get("token", "")): str,
                    vol.Required("org_id", default=entry.data.get("org_id", "")): str,
                    vol.Optional("user_id", default=uid_default): str,
                    vol.Optional("scan_interval", default=entry.data.get("scan_interval", 30)): vol.All(
                        vol.Coerce(int), vol.Range(min=15)
                    ),
                    vol.Optional("alarm_duration", default=entry.data.get("alarm_duration", 120)): vol.All(
                        vol.Coerce(int), vol.Range(min=1)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return GroupAlarmOptionsFlowHandler(config_entry)


class GroupAlarmOptionsFlowHandler(config_entries.OptionsFlow):
    """Ermöglicht das Ändern der Werte über 'Konfigurieren'."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            user_input["user_id"] = int(user_input["user_id"]) if user_input.get("user_id") else 0
            return self.async_create_entry(title="", data=user_input)

        scan = self.config_entry.options.get(
            "scan_interval", self.config_entry.data.get("scan_interval", 30)
        )
        dur = self.config_entry.options.get(
            "alarm_duration", self.config_entry.data.get("alarm_duration", 120)
        )
        saved_uid = self.config_entry.options.get(
            "user_id", self.config_entry.data.get("user_id", 0)
        )
        uid_default = str(saved_uid) if saved_uid else ""

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional("user_id", default=uid_default): str,
                    vol.Optional("scan_interval", default=scan): vol.All(
                        vol.Coerce(int), vol.Range(min=15)
                    ),
                    vol.Optional("alarm_duration", default=dur): vol.All(
                        vol.Coerce(int), vol.Range(min=1)
                    ),
                }
            ),
        )