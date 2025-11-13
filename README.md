# Bromont Mountain Conditions - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Home Assistant custom integration that provides real-time ski conditions from Bromont Mountain (Ski Bromont) in Quebec, Canada.

## Features

- **Real-time Updates**: Automatically fetches current mountain conditions
- **Comprehensive Data**: 30+ sensors covering all aspects of the mountain
- **OpenStreetMap Integration**: Individual trail sensors with OSM way IDs for mapping
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

### Individual Trail Sensors (98+ sensors)
Each trail at Bromont gets its own sensor with:
- Current status (open/closed)
- Day and night availability
- Difficulty level
- Area/sector location
- **OpenStreetMap Integration**:
  - OSM way ID for mapping
  - Direct link to view trail on OpenStreetMap
  - Geographic coordinates for map display

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

## OpenStreetMap Integration

Each individual trail sensor now includes OpenStreetMap data with **geographic coordinates**, allowing you to:
- **Display trails on Home Assistant maps** using built-in map cards
- View actual trail paths with full geometry data
- Link directly to trail information on OpenStreetMap
- Export trail data to GeoJSON for advanced mapping

### Trail Sensor Attributes

Every trail sensor includes these attributes:

**Bromont Data:**
- `trail_number`: Trail number from Bromont
- `trail_name`: Trail name
- `area`: Mountain sector (e.g., "Versant du Village")
- `difficulty`: Bromont difficulty rating
- `day_status`: Day operation status
- `night_status`: Night operation status

**Geographic Data (when OSM match found):**
- `latitude`: Center point latitude for map display
- `longitude`: Center point longitude for map display
- `geojson`: Full trail path as GeoJSON LineString
- `trail_coordinates`: Array of [lat, lon] points along the trail
- `trail_points_count`: Number of coordinate points in the trail

**OpenStreetMap Metadata (when available):**
- `osm_id`: OpenStreetMap way ID (unique identifier)
- `osm_url`: Direct link to view trail on OpenStreetMap

### Example: Using Trail Data in Dashboard

```yaml
type: entities
title: Cowansville Trail
entities:
  - entity: sensor.ski_bromont_trail_47_cowansville
    name: Status
  - entity: sensor.ski_bromont_trail_47_cowansville
    type: attribute
    attribute: difficulty
    name: Difficulty
  - entity: sensor.ski_bromont_trail_47_cowansville
    type: attribute
    attribute: osm_id
    name: OpenStreetMap ID
  - entity: sensor.ski_bromont_trail_47_cowansville
    type: attribute
    attribute: osm_url
    name: View on OSM
```

### Displaying Trails on a Map

Trail sensors with OSM data now include `latitude` and `longitude` attributes, making them compatible with Home Assistant's built-in map card!

**Simple Map Display (Built-in Map Card):**

```yaml
type: map
title: Bromont Trails
default_zoom: 14
entities:
  - sensor.ski_bromont_trail_47_cowansville
  - sensor.ski_bromont_trail_48_sherbrooke
  # Add more trail entities...
```

**Auto-populate All Trails with Coordinates:**

```yaml
type: custom:auto-entities
card:
  type: map
  title: All Bromont Trails
  default_zoom: 14
filter:
  include:
    - entity_id: sensor.ski_bromont_trail_*
      attributes:
        latitude: ">0"  # Only trails with coordinates
```

**Advanced Mapping Options:**

1. **Built-in Map Card** - Works immediately with latitude/longitude attributes
2. **Custom Map Cards** - Install from HACS for advanced features:
   - [Leaflet Map Card](https://github.com/Leaflet/Leaflet) - Display full trail paths using GeoJSON
   - [Map Card](https://github.com/nathan-gs/ha-map-card) - Enhanced mapping features
3. **GeoJSON Export** - Use `scripts/export_trails_geojson.py` to export trail data

See `dashboards/trails_map_with_coordinates.yaml` for complete examples and `dashboards/osm_trails_map_guide.md` for advanced mapping techniques.

### Trail Sensor Naming

Trail sensors use one of two naming patterns:
- `sensor.ski_bromont_trail_osm_{osm_id}` - When matched with OpenStreetMap data
- `sensor.ski_bromont_trail_{number}_{name}` - When no OSM match is found

This ensures each trail has a unique, stable entity ID that can be used in automations and dashboards.

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
├── osm_data.py         # OpenStreetMap integration with coordinates
├── strings.json        # UI strings
└── translations/
    ├── en.json         # English translations
    └── fr.json         # French translations

dashboards/
├── bromont_dashboard.yaml           # Main dashboard example
├── trails_map_example.yaml          # Trail mapping examples
├── trails_map_with_coordinates.yaml # Map display with GPS coordinates
├── osm_trails_map_guide.md          # Advanced mapping guide
└── README.md                        # Dashboard documentation

scripts/
└── export_trails_geojson.py         # Export trail data to GeoJSON
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
- Trail geometry data from [OpenStreetMap](https://www.openstreetmap.org)
- Built for the Home Assistant community

---

**Note**: This is an unofficial integration and is not affiliated with or endorsed by Ski Bromont.