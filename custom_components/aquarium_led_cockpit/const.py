"""Constants for the Aquarium LED Cockpit integration."""

DOMAIN = "aquarium_led_cockpit"

PLATFORMS = ["sensor"]

CONF_INSTALL_BLUEPRINT = "install_blueprint"
CONF_EXPORT_DASHBOARD_SNIPPETS = "export_dashboard_snippets"
CONF_EXPORT_LEGACY_FILES = "export_legacy_files"
CONF_OVERWRITE_EXISTING = "overwrite_existing"
CONF_AUTO_INSTALL = "auto_install"

CONF_STATUS_JSON = "status_json"
CONF_CONFIG_ENTRY_ID = "config_entry_id"

DEFAULT_INSTALL_BLUEPRINT = True
DEFAULT_EXPORT_DASHBOARD_SNIPPETS = True
DEFAULT_EXPORT_LEGACY_FILES = False
DEFAULT_OVERWRITE_EXISTING = False
DEFAULT_AUTO_INSTALL = True

DATA_RUNTIME = "runtime"
DATA_SERVICES_REGISTERED = "services_registered"

SERVICE_INSTALL_RESOURCES = "install_resources"
SERVICE_SET_DASHBOARD_STATUS = "set_dashboard_status"

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}_status"

STATUS_SENSOR_UNIQUE_ID = f"{DOMAIN}_status"
STATUS_SENSOR_NAME = "Aquarium LED Cockpit Status"
