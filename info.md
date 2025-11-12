# Bromont Mountain Conditions

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant custom integration that provides real-time ski conditions from Bromont Mountain (Ski Bromont) in Quebec, Canada.

## Features

- **Real-time Updates**: Automatically fetches current mountain conditions
- **Comprehensive Data**: 30+ sensors covering all aspects of the mountain
- **Easy Configuration**: Simple UI-based setup through Home Assistant
- **Customizable**: Adjust update frequency from 1-60 minutes

## Sensors Provided

### Snow Conditions
- 24h, 48h, 7-day, and total snow accumulation
- Surface conditions
- Base depth
- Coverage percentage

### Mountain Operations
- Lifts (day/night)
- Trails (day/night)
- Glades (day/night)
- Snow parks (day/night)
- Alpine hiking trails (day/night)
- Snowshoeing trails (day/night)
- Parking availability (day/night)

### Terrain Information
- Status for all 7 mountain sectors:
  - Versant du Village
  - Versant du Lac
  - Versant des Cantons
  - Versant des Épinettes
  - Mont Soleil
  - Versant du Midi
  - Versant de la Côte Ouest

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant
8. Go to Settings → Devices & Services → Add Integration
9. Search for "Bromont Mountain Conditions"
10. Configure the update interval (default: 5 minutes)

### Manual Installation

1. Copy the `custom_components/bromont` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Bromont Mountain Conditions"
5. Configure the update interval

## Configuration

After installation, add the integration through the UI:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Bromont Mountain Conditions**
4. Set your preferred update interval (1-60 minutes, default: 5)

You can modify the update interval later through the integration's options.

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
  - sensor.bromont_status
  - sensor.bromont_snow_24h
  - sensor.bromont_trails_day
  - sensor.bromont_lifts_day
  - sensor.bromont_surface_condition
```

### Example Automation

```yaml
automation:
  - alias: "Notify on Fresh Snow"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bromont_snow_24h
        above: 10
    action:
      - service: notify.mobile_app
        data:
          message: "Fresh powder at Bromont! {{ states('sensor.bromont_snow_24h') }}cm in 24h"
```

## Data Source

This integration scrapes data directly from the official Ski Bromont website at https://www.skibromont.com/en/conditions

## Support

For issues, feature requests, or contributions, please visit the [GitHub repository](https://github.com/zopanix/bromont-ha-integration).

## License

This project is licensed under the MIT License.