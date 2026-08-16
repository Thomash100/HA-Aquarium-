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
CONF_MOON_ENTITY = "moon_entity"
CONF_PRICE_ENTITY = "price_entity"
CONF_BATTERY_SOC_ENTITY = "battery_soc_entity"
CONF_SOLAR_POWER_ENTITY = "solar_power_entity"
CONF_BATTERY_FULL_THRESHOLD = "battery_full_threshold"
CONF_TRANSITION_SECONDS = "transition_seconds"

CONF_STATUS_JSON = "status_json"
CONF_CONFIG_ENTRY_ID = "config_entry_id"
CONF_PHASE = "phase"
CONF_RGBW_COLOR = "rgbw_color"

DEFAULT_EXPORT_FRONTEND_RESOURCES = True
DEFAULT_OVERWRITE_EXISTING = False
DEFAULT_AUTO_INSTALL = True
DEFAULT_SUN_ENTITY = "sun.sun"
DEFAULT_MOON_ENTITY = "sensor.moon_phase"
DEFAULT_TRANSITION_SECONDS = 30
DEFAULT_DAY_BRIGHTNESS = 90
DEFAULT_NIGHT_BRIGHTNESS = 2
DEFAULT_PRICE_DIMMING = 40
DEFAULT_BATTERY_FULL_THRESHOLD = 95
DEFAULT_CLOUD_STRENGTH = 45
DEFAULT_SIMULATION_TIME = 360
DEFAULT_SUNRISE_OFFSET_HOURS = 0
DEFAULT_SUNRISE_DURATION_MINUTES = 60
DEFAULT_SUNSET_DURATION_MINUTES = 90

DATA_RUNTIMES = "runtimes"
DATA_SERVICES_REGISTERED = "services_registered"

SERVICE_INSTALL_RESOURCES = "install_resources"
SERVICE_SET_DASHBOARD_STATUS = "set_dashboard_status"
SERVICE_SET_TRANSITION_COLOR = "set_transition_color"

STORAGE_VERSION = 1
STORAGE_KEY_PREFIX = f"{DOMAIN}_entry"

STATUS_SENSOR_UNIQUE_ID = f"{DOMAIN}_status"
STATUS_SENSOR_NAME = "Aquarium LED Cockpit Status"

CONTROL_ENABLED = "enabled"
CONTROL_SIMULATION = "simulation"
CONTROL_TIME_LAPSE = "time_lapse"
CONTROL_AQUARIUM_PREVIEW = "aquarium_preview"
CONTROL_DAY_BRIGHTNESS = "day_brightness_pct"
CONTROL_NIGHT_BRIGHTNESS = "night_brightness_pct"
CONTROL_PRICE_DIMMING = "price_dimming_pct"
CONTROL_CLOUD_STRENGTH = "cloud_strength_pct"
CONTROL_SIMULATION_TIME = "simulation_time_minutes"
# The stored key and entity unique ID stay unchanged for upgrade compatibility.
CONTROL_TIME_LAPSE_DURATION = "simulation_step_minutes"
CONTROL_SUNRISE_OFFSET = "sunrise_offset_hours"
CONTROL_SUNRISE_DURATION = "sunrise_duration_minutes"
CONTROL_SUNSET_DURATION = "sunset_duration_minutes"
CONTROL_SUNRISE_RGBW = "sunrise_rgbw"
CONTROL_SUNSET_RGBW = "sunset_rgbw"
