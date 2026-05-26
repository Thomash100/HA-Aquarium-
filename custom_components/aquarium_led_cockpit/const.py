"""Constants for the Aquarium LED Cockpit integration."""

DOMAIN = "aquarium_led_cockpit"

PLATFORMS = ["sensor", "switch", "number"]

CONF_NAME = "name"
CONF_EXPORT_FRONTEND_RESOURCES = "export_frontend_resources"
CONF_OVERWRITE_EXISTING = "overwrite_existing"
CONF_AUTO_INSTALL = "auto_install"
CONF_RGBW_LIGHTS = "rgbw_lights"
CONF_WHITE_LIGHTS = "white_lights"
CONF_WEATHER_ENTITY = "weather_entity"
CONF_SUN_ENTITY = "sun_entity"
CONF_PRICE_ENTITY = "price_entity"
CONF_TRANSITION_SECONDS = "transition_seconds"

CONF_STATUS_JSON = "status_json"
CONF_CONFIG_ENTRY_ID = "config_entry_id"

DEFAULT_EXPORT_FRONTEND_RESOURCES = True
DEFAULT_OVERWRITE_EXISTING = False
DEFAULT_AUTO_INSTALL = True
DEFAULT_SUN_ENTITY = "sun.sun"
DEFAULT_TRANSITION_SECONDS = 30
DEFAULT_DAY_BRIGHTNESS = 90
DEFAULT_NIGHT_BRIGHTNESS = 2
DEFAULT_PRICE_DIMMING = 40
DEFAULT_CLOUD_STRENGTH = 45
DEFAULT_SIMULATION_TIME = 360
DEFAULT_SIMULATION_STEP = 15

DATA_RUNTIMES = "runtimes"
DATA_SERVICES_REGISTERED = "services_registered"

SERVICE_INSTALL_RESOURCES = "install_resources"
SERVICE_SET_DASHBOARD_STATUS = "set_dashboard_status"

STORAGE_VERSION = 1
STORAGE_KEY_PREFIX = f"{DOMAIN}_entry"

STATUS_SENSOR_UNIQUE_ID = f"{DOMAIN}_status"
STATUS_SENSOR_NAME = "Aquarium LED Cockpit Status"

CONTROL_ENABLED = "enabled"
CONTROL_SIMULATION = "simulation"
CONTROL_TIME_LAPSE = "time_lapse"
CONTROL_DAY_BRIGHTNESS = "day_brightness_pct"
CONTROL_NIGHT_BRIGHTNESS = "night_brightness_pct"
CONTROL_PRICE_DIMMING = "price_dimming_pct"
CONTROL_CLOUD_STRENGTH = "cloud_strength_pct"
CONTROL_SIMULATION_TIME = "simulation_time_minutes"
CONTROL_SIMULATION_STEP = "simulation_step_minutes"
