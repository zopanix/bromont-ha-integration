"""Sensor platform for Bromont Mountain Conditions."""

from __future__ import annotations

import re

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, ATTRIBUTION


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bromont sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        # Status sensors
        BromontStatusSensor(coordinator),
        BromontDateSensor(coordinator),
        BromontLastUpdateSensor(coordinator),
        # Snow accumulation sensors
        BromontSnow24hSensor(coordinator),
        BromontSnow48hSensor(coordinator),
        BromontSnow7DaysSensor(coordinator),
        BromontSnowTotalSensor(coordinator),
        # Conditions sensors
        BromontSurfaceSensor(coordinator),
        BromontBaseSensor(coordinator),
        BromontCoverageSensor(coordinator),
        # Lifts sensors
        BromontLiftsDaySensor(coordinator),
        BromontLiftsNightSensor(coordinator),
        # Trails sensors
        BromontTrailsDaySensor(coordinator),
        BromontTrailsNightSensor(coordinator),
        # Glades sensors
        BromontGladesDaySensor(coordinator),
        BromontGladesNightSensor(coordinator),
        # Snow parks sensors
        BromontParksDaySensor(coordinator),
        BromontParksNightSensor(coordinator),
        # Alpine hiking sensors
        BromontHikingDaySensor(coordinator),
        BromontHikingNightSensor(coordinator),
        # Snowshoeing sensors
        BromontSnowshoeingDaySensor(coordinator),
        BromontSnowshoeingNightSensor(coordinator),
        # Parking sensors
        BromontParkingDaySensor(coordinator),
        BromontParkingNightSensor(coordinator),
        # Terrain sensors
        BromontTerrainVillageSensor(coordinator),
        BromontTerrainLacSensor(coordinator),
        BromontTerrainCantonsSensor(coordinator),
        BromontTerrainEpinettesSensor(coordinator),
        BromontTerrainMontSoleilSensor(coordinator),
        BromontTerrainMidiSensor(coordinator),
        BromontTerrainCoteOuestSensor(coordinator),
    ]

    # Add individual trail sensors
    trails_data = coordinator.data.get("trails", {}).get("by_area", {})
    for area, trails in trails_data.items():
        for trail in trails:
            sensors.append(BromontTrailSensor(coordinator, area, trail))

    async_add_entities(sensors)


class BromontSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Bromont sensors."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = False

    def __init__(self, coordinator, sensor_type: str, name: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"Ski Bromont {name}"
        self._attr_unique_id = f"ski_bromont_{sensor_type}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "bromont_mountain")},
            name="Ski Bromont",
            manufacturer="Ski Bromont",
            model="Mountain Conditions",
            configuration_url="https://www.skibromont.com",
        )


# Status Sensors
class BromontStatusSensor(BromontSensorBase):
    """Sensor for mountain status."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "status", "Status")
        self._attr_icon = "mdi:clock-outline"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("hours", {}).get("status")


class BromontDateSensor(BromontSensorBase):
    """Sensor for current date."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "date", "Date")
        self._attr_icon = "mdi:calendar"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("date")


class BromontLastUpdateSensor(BromontSensorBase):
    """Sensor for last update time."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "last_update", "Last Update")
        self._attr_icon = "mdi:update"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("last_update")


# Snow Accumulation Sensors
class BromontSnow24hSensor(BromontSensorBase):
    """Sensor for 24h snow accumulation."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "snow_24h", "Snow 24h")
        self._attr_icon = "mdi:snowflake"
        self._attr_native_unit_of_measurement = "cm"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state."""
        accumulations = self.coordinator.data.get("accumulations", {})
        value = accumulations.get("24h", {}).get("metric", "0 cm")
        # Extract numeric value
        return value.replace(" cm", "").strip()


class BromontSnow48hSensor(BromontSensorBase):
    """Sensor for 48h snow accumulation."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "snow_48h", "Snow 48h")
        self._attr_icon = "mdi:snowflake"
        self._attr_native_unit_of_measurement = "cm"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state."""
        accumulations = self.coordinator.data.get("accumulations", {})
        return accumulations.get("48 h", {}).get("metric", "0")


class BromontSnow7DaysSensor(BromontSensorBase):
    """Sensor for 7 days snow accumulation."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "snow_7days", "Snow 7 Days")
        self._attr_icon = "mdi:snowflake"
        self._attr_native_unit_of_measurement = "cm"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state."""
        accumulations = self.coordinator.data.get("accumulations", {})
        return accumulations.get("7 jours", {}).get("metric", "0")


class BromontSnowTotalSensor(BromontSensorBase):
    """Sensor for total snow accumulation."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "snow_total", "Snow Total")
        self._attr_icon = "mdi:snowflake"
        self._attr_native_unit_of_measurement = "cm"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state."""
        accumulations = self.coordinator.data.get("accumulations", {})
        return accumulations.get("Total", {}).get("metric", "0")


# Conditions Sensors
class BromontSurfaceSensor(BromontSensorBase):
    """Sensor for surface condition."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "surface", "Surface Condition")
        self._attr_icon = "mdi:texture"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("conditions", {}).get("surface")


class BromontBaseSensor(BromontSensorBase):
    """Sensor for base depth."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "base", "Base Depth")
        self._attr_icon = "mdi:ruler"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("conditions", {}).get("base")


class BromontCoverageSensor(BromontSensorBase):
    """Sensor for coverage."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "coverage", "Coverage")
        self._attr_icon = "mdi:percent"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("conditions", {}).get("couverture")


# Lifts Sensors
class BromontLiftsDaySensor(BromontSensorBase):
    """Sensor for lifts open during day."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "lifts_day", "Lifts Day")
        self._attr_icon = "mdi:ski-lift"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("lifts", {}).get("summary", {})
        day = summary.get("day", {})
        return f"{day.get('open', '0')}/{day.get('total', '0')}"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        summary = self.coordinator.data.get("lifts", {}).get("summary", {})
        day = summary.get("day", {})
        return {
            "open": day.get("open", "0"),
            "total": day.get("total", "0"),
        }


class BromontLiftsNightSensor(BromontSensorBase):
    """Sensor for lifts open at night."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "lifts_night", "Lifts Night")
        self._attr_icon = "mdi:ski-lift"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("lifts", {}).get("summary", {})
        night = summary.get("night", {})
        return f"{night.get('open', '0')}/{night.get('total', '0')}"


# Trails Sensors
class BromontTrailsDaySensor(BromontSensorBase):
    """Sensor for trails open during day."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "trails_day", "Trails Day")
        self._attr_icon = "mdi:ski"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("trails", {}).get("summary", {})
        day = summary.get("day", {})
        return f"{day.get('open', '0')}/{day.get('total', '0')}"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        summary = self.coordinator.data.get("trails", {}).get("summary", {})
        day = summary.get("day", {})
        return {
            "open": day.get("open", "0"),
            "total": day.get("total", "0"),
        }


class BromontTrailsNightSensor(BromontSensorBase):
    """Sensor for trails open at night."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "trails_night", "Trails Night")
        self._attr_icon = "mdi:ski"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("trails", {}).get("summary", {})
        night = summary.get("night", {})
        return f"{night.get('open', '0')}/{night.get('total', '0')}"


# Glades Sensors
class BromontGladesDaySensor(BromontSensorBase):
    """Sensor for glades open during day."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "glades_day", "Glades Day")
        self._attr_icon = "mdi:pine-tree"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("glades", {}).get("summary", {})
        day = summary.get("day", {})
        return f"{day.get('open', '0')}/{day.get('total', '0')}"


class BromontGladesNightSensor(BromontSensorBase):
    """Sensor for glades open at night."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "glades_night", "Glades Night")
        self._attr_icon = "mdi:pine-tree"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("glades", {}).get("summary", {})
        night = summary.get("night", {})
        return f"{night.get('open', '0')}/{night.get('total', '0')}"


# Snow Parks Sensors
class BromontParksDaySensor(BromontSensorBase):
    """Sensor for snow parks open during day."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "parks_day", "Snow Parks Day")
        self._attr_icon = "mdi:terrain"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("snow_parks", {}).get("summary", {})
        day = summary.get("day", {})
        return f"{day.get('open', '0')}/{day.get('total', '0')}"


class BromontParksNightSensor(BromontSensorBase):
    """Sensor for snow parks open at night."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "parks_night", "Snow Parks Night")
        self._attr_icon = "mdi:terrain"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("snow_parks", {}).get("summary", {})
        night = summary.get("night", {})
        return f"{night.get('open', '0')}/{night.get('total', '0')}"


# Alpine Hiking Sensors
class BromontHikingDaySensor(BromontSensorBase):
    """Sensor for alpine hiking trails open during day."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "hiking_day", "Alpine Hiking Day")
        self._attr_icon = "mdi:hiking"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("alpine_hiking", {}).get("summary", {})
        day = summary.get("day", {})
        return f"{day.get('open', '0')}/{day.get('total', '0')}"


class BromontHikingNightSensor(BromontSensorBase):
    """Sensor for alpine hiking trails open at night."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "hiking_night", "Alpine Hiking Night")
        self._attr_icon = "mdi:hiking"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("alpine_hiking", {}).get("summary", {})
        night = summary.get("night", {})
        return f"{night.get('open', '0')}/{night.get('total', '0')}"


# Snowshoeing Sensors
class BromontSnowshoeingDaySensor(BromontSensorBase):
    """Sensor for snowshoeing trails open during day."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "snowshoeing_day", "Snowshoeing Day")
        self._attr_icon = "mdi:shoe-print"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("snowshoeing", {}).get("summary", {})
        day = summary.get("day", {})
        return f"{day.get('open', '0')}/{day.get('total', '0')}"


class BromontSnowshoeingNightSensor(BromontSensorBase):
    """Sensor for snowshoeing trails open at night."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "snowshoeing_night", "Snowshoeing Night")
        self._attr_icon = "mdi:shoe-print"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("snowshoeing", {}).get("summary", {})
        night = summary.get("night", {})
        return f"{night.get('open', '0')}/{night.get('total', '0')}"


# Parking Sensors
class BromontParkingDaySensor(BromontSensorBase):
    """Sensor for parking open during day."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "parking_day", "Parking Day")
        self._attr_icon = "mdi:parking"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("parking", {}).get("summary", {})
        day = summary.get("day", {})
        return f"{day.get('open', '0')}/{day.get('total', '0')}"


class BromontParkingNightSensor(BromontSensorBase):
    """Sensor for parking open at night."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "parking_night", "Parking Night")
        self._attr_icon = "mdi:parking"

    @property
    def native_value(self):
        """Return the state."""
        summary = self.coordinator.data.get("parking", {}).get("summary", {})
        night = summary.get("night", {})
        return f"{night.get('open', '0')}/{night.get('total', '0')}"


# Terrain Sensors
class BromontTerrainVillageSensor(BromontSensorBase):
    """Sensor for Versant du Village terrain."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "terrain_village", "Terrain Village")
        self._attr_icon = "mdi:mountain"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("terrain", {}).get("Versant du Village")


class BromontTerrainLacSensor(BromontSensorBase):
    """Sensor for Versant du Lac terrain."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "terrain_lac", "Terrain Lac")
        self._attr_icon = "mdi:mountain"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("terrain", {}).get("Versant du Lac")


class BromontTerrainCantonsSensor(BromontSensorBase):
    """Sensor for Versant des Cantons terrain."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "terrain_cantons", "Terrain Cantons")
        self._attr_icon = "mdi:mountain"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("terrain", {}).get("Versant des Cantons")


class BromontTerrainEpinettesSensor(BromontSensorBase):
    """Sensor for Versant des Épinettes terrain."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "terrain_epinettes", "Terrain Épinettes")
        self._attr_icon = "mdi:mountain"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("terrain", {}).get("Versant des Épinettes")


class BromontTerrainMontSoleilSensor(BromontSensorBase):
    """Sensor for Mont Soleil terrain."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "terrain_mont_soleil", "Terrain Mont Soleil")
        self._attr_icon = "mdi:mountain"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("terrain", {}).get("Mont soleil")


class BromontTerrainMidiSensor(BromontSensorBase):
    """Sensor for Versant du Midi terrain."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "terrain_midi", "Terrain Midi")
        self._attr_icon = "mdi:mountain"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("terrain", {}).get("Versant du Midi")


class BromontTerrainCoteOuestSensor(BromontSensorBase):
    """Sensor for Versant de la Côte Ouest terrain."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "terrain_cote_ouest", "Terrain Côte Ouest")
        self._attr_icon = "mdi:mountain"

    @property
    def native_value(self):
        """Return the state."""
        return self.coordinator.data.get("terrain", {}).get("Versant de la Côte Ouest")


# Individual Trail Sensors
class BromontTrailSensor(BromontSensorBase):
    """Sensor for individual trail status."""

    def __init__(self, coordinator, area: str, trail: dict):
        """Initialize the sensor."""
        self._area = area
        self._trail = trail
        trail_name = trail.get("name", "Unknown")
        trail_number = trail.get("number", "")
        trail_difficulty = trail.get("difficulty", "")

        # Try to match with OSM data (pass difficulty for better matching)
        self._osm_data = None
        if hasattr(coordinator, 'osm_data') and coordinator.osm_data:
            self._osm_data = coordinator.osm_data.match_trail(
                trail_name,
                trail_number,
                trail_difficulty
            )

        # Create a safe sensor ID from trail name and number
        # If we have OSM data, use the OSM way ID as the object_id
        if self._osm_data and self._osm_data.get("osm_id"):
            sensor_id = f"trail_osm_{self._osm_data['osm_id']}"
        else:
            safe_name = re.sub(r"[^a-z0-9_]", "_", trail_name.lower())
            safe_name = re.sub(r"_+", "_", safe_name).strip("_")
            sensor_id = (
                f"trail_{trail_number}_{safe_name}"
                if trail_number
                else f"trail_{safe_name}"
            )

        super().__init__(coordinator, sensor_id, f"Trail: {trail_name}")
        self._attr_icon = "mdi:ski"

    @property
    def native_value(self):
        """Return the state."""
        # Get current trail data from coordinator
        trails_data = self.coordinator.data.get("trails", {}).get("by_area", {})
        area_trails = trails_data.get(self._area, [])

        # Find the matching trail by number or name
        trail_number = self._trail.get("number")
        trail_name = self._trail.get("name")

        for trail in area_trails:
            if trail.get("number") == trail_number and trail.get("name") == trail_name:
                return trail.get("day", "Unknown")

        return "Unknown"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        # Get current trail data from coordinator
        trails_data = self.coordinator.data.get("trails", {}).get("by_area", {})
        area_trails = trails_data.get(self._area, [])

        # Find the matching trail
        trail_number = self._trail.get("number")
        trail_name = self._trail.get("name")

        attributes = {
            "trail_number": self._trail.get("number", ""),
            "trail_name": self._trail.get("name", ""),
            "area": self._area,
            "difficulty": "Unknown",
            "day_status": "Unknown",
            "night_status": "Unknown",
        }

        # Update with current trail data
        for trail in area_trails:
            if trail.get("number") == trail_number and trail.get("name") == trail_name:
                attributes.update({
                    "difficulty": trail.get("difficulty", "Unknown"),
                    "day_status": trail.get("day", "Unknown"),
                    "night_status": trail.get("night", "-"),
                })
                break

        # Add OSM data if available
        if self._osm_data:
            attributes.update({
                "osm_id": self._osm_data.get("osm_id"),
                "osm_url": f"https://www.openstreetmap.org/way/{self._osm_data.get('osm_id')}",
            })
            
            # Add geographic data for map display
            center = self._osm_data.get("center")
            if center:
                attributes["latitude"] = center[0]
                attributes["longitude"] = center[1]
            
            # Add full trail path as GeoJSON for advanced mapping
            geojson = self._osm_data.get("geojson")
            if geojson:
                attributes["geojson"] = geojson
            
            # Add all coordinates for custom visualizations
            coordinates = self._osm_data.get("coordinates")
            if coordinates:
                attributes["trail_coordinates"] = coordinates
                attributes["trail_points_count"] = len(coordinates)

        return attributes
