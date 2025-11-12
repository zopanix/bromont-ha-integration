"""The Bromont Mountain Conditions integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .scraper import BromontScraper
from .osm_data import OSMTrailData

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bromont Mountain Conditions from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create the scraper
    scraper = BromontScraper()

    # Create OSM data fetcher
    osm_data = OSMTrailData()
    
    # Fetch OSM data once at startup (it doesn't change often)
    try:
        await osm_data.fetch_trails()
        _LOGGER.info("Successfully fetched OpenStreetMap trail data")
    except Exception as e:
        _LOGGER.warning(f"Failed to fetch OSM data, continuing without it: {e}")

    # Create the coordinator
    coordinator = BromontDataUpdateCoordinator(
        hass,
        scraper=scraper,
        osm_data=osm_data,
        update_interval=timedelta(minutes=entry.data.get("update_interval", 5)),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class BromontDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Bromont data."""

    def __init__(
        self,
        hass: HomeAssistant,
        scraper: BromontScraper,
        osm_data: OSMTrailData,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.scraper = scraper
        self.osm_data = osm_data

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from Bromont."""
        try:
            data = await self.scraper.scrape()
            if not data:
                raise UpdateFailed("Failed to fetch data from Bromont Mountain")
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Bromont API: {err}") from err
