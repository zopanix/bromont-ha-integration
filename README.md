# Bromont Mountain Conditions - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Home Assistant custom integration that provides real-time ski conditions from Bromont Mountain (Ski Bromont) in Quebec, Canada.

## Features

- **Real-time Updates**: Automatically fetches current mountain conditions
- **Comprehensive Data**: 30+ sensors covering all aspects of the mountain
- **Easy Configuration**: Simple UI-based setup through Home Assistant
- **Customizable**: Adjust update frequency from 1-60 minutes
- **HACS Compatible**: Easy installation and updates through HACS

## Sensors Provided

### Snow Conditions (4 sensors)
- 24h, 48h, 7-day, and total snow accumulation (in cm)
- Surface conditions
- Base depth
- Coverage percentage

### Mountain Operations (14 sensors)
- **Lifts**: Day and night operations
- **Trails**: Day and night operations
- **Glades**: Day and night operations
- **Snow Parks**: Day and night operations
- **Alpine Hiking**: Day and night trail availability
- **Snowshoeing**: Day and night trail availability
- **Parking**: Day and night availability

### Terrain Information (7 sensors)
Status for all mountain sectors:
- Versant du Village
- Versant du Lac
- Versant des Cantons
- Versant des Épinettes
- Mont Soleil
- Versant du Midi
- Versant de la Côte Ouest

### Status Sensors (3 sensors)
- Mountain status (open/closed)
- Current date
- Last update timestamp

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/zopanix/bromont-ha-integration`
6. Select "Integration" as the category
7. Click "Install"
8. Restart Home Assistant
9. Go to **Settings** → **Devices & Services** → **Add Integration**
10. Search for "Bromont Mountain Conditions"
11. Configure the update interval (default: 5 minutes)

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `custom_components/bromont` folder to your Home Assistant's `config/custom_components/` directory
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for "Bromont Mountain Conditions"
6. Configure the update interval

## Configuration

After installation, add the integration through the UI:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Bromont Mountain Conditions**
4. Set your preferred update interval (1-60 minutes, default: 5)

You can modify the update interval later by clicking "Configure" on the integration.

## Usage

All sensors will be automatically created under a single device called "Bromont Mountain". You can use these sensors in:

- Dashboards and cards
- Automations
- Scripts
- Templates

### Example Dashboard Card

```yaml
type: entities
title: Bromont Conditions
entities:
  - sensor.ski_bromont_status
  - sensor.ski_bromont_snow_24h
  - sensor.ski_bromont_trails_day
  - sensor.ski_bromont_lifts_day
  - sensor.ski_bromont_surface
  - sensor.ski_bromont_base
```

### Example Glance Card

```yaml
type: glance
title: Bromont Quick View
entities:
  - entity: sensor.ski_bromont_snow_24h
    name: 24h Snow
  - entity: sensor.ski_bromont_trails_day
    name: Trails
  - entity: sensor.ski_bromont_lifts_day
    name: Lifts
  - entity: sensor.ski_bromont_status
    name: Status
```

### Example Automation

```yaml
automation:
  - alias: "Notify on Fresh Snow"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ski_bromont_snow_24h
        above: 10
    action:
      - service: notify.mobile_app
        data:
          message: "Fresh powder at Bromont! {{ states('sensor.ski_bromont_snow_24h') }}cm in 24h"
          title: "Powder Alert! 🎿"
```

### Example Template Sensor

```yaml
template:
  - sensor:
      - name: "Bromont Conditions Summary"
        state: >
          {% set snow = states('sensor.ski_bromont_snow_24h') %}
          {% set trails = states('sensor.ski_bromont_trails_day') %}
          {% set status = states('sensor.ski_bromont_status') %}
          {{ status }}: {{ trails }} trails, {{ snow }}cm fresh snow
```

## Available Sensors

| Sensor | Description | Unit |
|--------|-------------|------|
| `sensor.ski_bromont_status` | Mountain status (open/closed) | - |
| `sensor.ski_bromont_date` | Current date | - |
| `sensor.ski_bromont_last_update` | Last update timestamp | - |
| `sensor.ski_bromont_snow_24h` | Snow accumulation (24h) | cm |
| `sensor.ski_bromont_snow_48h` | Snow accumulation (48h) | cm |
| `sensor.ski_bromont_snow_7days` | Snow accumulation (7 days) | cm |
| `sensor.ski_bromont_snow_total` | Total snow accumulation | cm |
| `sensor.ski_bromont_surface` | Surface condition | - |
| `sensor.ski_bromont_base` | Base depth | - |
| `sensor.ski_bromont_coverage` | Coverage percentage | - |
| `sensor.ski_bromont_lifts_day` | Lifts open (day) | - |
| `sensor.ski_bromont_lifts_night` | Lifts open (night) | - |
| `sensor.ski_bromont_trails_day` | Trails open (day) | - |
| `sensor.ski_bromont_trails_night` | Trails open (night) | - |
| `sensor.ski_bromont_glades_day` | Glades open (day) | - |
| `sensor.ski_bromont_glades_night` | Glades open (night) | - |
| `sensor.ski_bromont_parks_day` | Snow parks open (day) | - |
| `sensor.ski_bromont_parks_night` | Snow parks open (night) | - |
| `sensor.ski_bromont_hiking_day` | Alpine hiking trails (day) | - |
| `sensor.ski_bromont_hiking_night` | Alpine hiking trails (night) | - |
| `sensor.ski_bromont_snowshoeing_day` | Snowshoeing trails (day) | - |
| `sensor.ski_bromont_snowshoeing_night` | Snowshoeing trails (night) | - |
| `sensor.ski_bromont_parking_day` | Parking availability (day) | - |
| `sensor.ski_bromont_parking_night` | Parking availability (night) | - |
| `sensor.ski_bromont_terrain_village` | Versant du Village status | % |
| `sensor.ski_bromont_terrain_lac` | Versant du Lac status | % |
| `sensor.ski_bromont_terrain_cantons` | Versant des Cantons status | % |
| `sensor.ski_bromont_terrain_epinettes` | Versant des Épinettes status | % |
| `sensor.ski_bromont_terrain_mont_soleil` | Mont Soleil status | % |
| `sensor.ski_bromont_terrain_midi` | Versant du Midi status | % |
| `sensor.ski_bromont_terrain_cote_ouest` | Versant de la Côte Ouest status | % |

## Data Source

This integration scrapes data directly from the official Ski Bromont website at https://www.skibromont.com/en/conditions

## Troubleshooting

### Integration not showing up
- Ensure you've restarted Home Assistant after installation
- Check the logs for any errors: **Settings** → **System** → **Logs**

### Sensors showing "Unknown" or "Unavailable"
- Check your internet connection
- Verify the Bromont website is accessible
- Check the integration logs for scraping errors
- Try increasing the update interval if you're getting rate-limited

### Update interval not working
- The interval must be between 1 and 60 minutes
- Changes require reconfiguring the integration

## Development

This integration includes:
- Async data coordinator for efficient updates
- Config flow for UI-based configuration
- Proper error handling and logging
- Device registry integration
- Translation support

### Project Structure
```
custom_components/bromont/
├── __init__.py          # Integration setup and coordinator
├── config_flow.py       # UI configuration flow
├── const.py            # Constants and defaults
├── manifest.json       # Integration metadata
├── scraper.py          # Web scraping logic
├── sensor.py           # Sensor platform
├── strings.json        # UI strings
└── translations/
    └── en.json         # English translations
```

## Legacy Add-on

This project was originally a Home Assistant add-on. The add-on files are still available in the repository for reference, but the integration is now the recommended installation method as it:
- Works on all Home Assistant installations (not just Supervisor)
- Provides better UI integration
- Offers easier configuration
- Has better performance

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, feature requests, or questions:
- Open an issue on [GitHub](https://github.com/zopanix/bromont-ha-integration/issues)
- Check existing issues for solutions

## Acknowledgments

- Data provided by [Ski Bromont](https://www.skibromont.com)
- Built for the Home Assistant community

---

**Note**: This is an unofficial integration and is not affiliated with or endorsed by Ski Bromont.