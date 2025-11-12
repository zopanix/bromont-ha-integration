# Bromont Mountain Dashboard for Home Assistant

This repository contains two TV-optimized dashboard configurations for the Bromont Mountain Conditions integration.

## 📺 Dashboard Versions

### 1. **bromont_dashboard.yaml** (Enhanced Version)
A feature-rich dashboard with custom cards for the best visual experience.

**Features:**
- Large, colorful status banner with gradient backgrounds
- Visual progress bars for terrain status
- Mushroom cards for modern, clean UI
- Color-coded indicators based on conditions
- Optimized for large TV displays

**Requirements:**
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom)
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod)

### 2. **bromont_dashboard_simple.yaml** (Simple Version)
A clean dashboard using only built-in Home Assistant cards.

**Features:**
- No custom cards required
- Works out-of-the-box
- Clean, organized layout
- All essential information displayed
- Perfect for quick setup

**Requirements:**
- None (uses only built-in cards)

## 🚀 Installation

### Step 1: Install Custom Cards (for Enhanced Version only)

If using the enhanced version, install these custom cards via HACS:

1. Open HACS in Home Assistant
2. Go to "Frontend"
3. Click the "+" button
4. Search and install:
   - **Mushroom Cards**
   - **Card Mod**
5. Restart Home Assistant

### Step 2: Copy Dashboard File

1. Choose which dashboard version you want to use
2. Copy the chosen YAML file to your Home Assistant configuration directory:
   - For enhanced: `dashboards/bromont_dashboard.yaml`
   - For simple: `dashboards/bromont_dashboard_simple.yaml`

### Step 3: Configure Lovelace

Add the following to your `configuration.yaml`:

```yaml
lovelace:
  mode: storage
  dashboards:
    bromont-tv:
      mode: yaml
      title: Bromont Mountain
      icon: mdi:ski
      filename: dashboards/bromont_dashboard.yaml  # or dashboards/bromont_dashboard_simple.yaml
```

### Step 4: Configure Weather Integration

The dashboard includes a weather widget. You need to configure a weather integration:

#### Option 1: Met.no (Free, No API Key Required)

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Met.no"
4. Configure with your location
5. The entity will be `weather.home` or similar

#### Option 2: OpenWeatherMap (Free API Key)

1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Go to **Settings** → **Devices & Services**
3. Click **Add Integration**
4. Search for "OpenWeatherMap"
5. Enter your API key and location

#### Option 3: AccuWeather (Free API Key)

1. Get a free API key from [AccuWeather](https://developer.accuweather.com/)
2. Go to **Settings** → **Devices & Services**
3. Click **Add Integration**
4. Search for "AccuWeather"
5. Enter your API key and location

### Step 5: Update Weather Entity (if needed)

If your weather entity is not named `weather.home`, update the dashboard YAML file:

1. Find all instances of `weather.home`
2. Replace with your actual weather entity name (e.g., `weather.openweathermap`)

You can find your weather entity name in:
- **Developer Tools** → **States** → Search for "weather."

### Step 6: Restart and Access

1. Restart Home Assistant
2. Navigate to the sidebar
3. Click on "Bromont Mountain" dashboard
4. For TV casting, use the dashboard URL in Kiosk mode

## 📱 TV Casting Options

### Option 1: Kiosk Mode URL

Access the dashboard in kiosk mode (hides sidebar and header):

```
http://your-home-assistant-url:8123/bromont-tv?kiosk
```

### Option 2: Fully Kiosk Browser (Android)

1. Install [Fully Kiosk Browser](https://www.fully-kiosk.com/) on your Android TV
2. Configure it to load your dashboard URL
3. Enable kiosk mode in settings
4. Set auto-refresh interval (recommended: 5 minutes)

### Option 3: Chrome Cast

1. Open the dashboard in Chrome browser
2. Click the three dots menu
3. Select "Cast"
4. Choose your TV/Chromecast device

### Option 4: Fire TV Silk Browser

1. Install Silk Browser on Fire TV
2. Navigate to your dashboard URL
3. Add to favorites for easy access

## 🎨 Customization

### Adjusting Font Sizes

For larger/smaller text on your TV, modify the `font-size` values in the YAML:

```yaml
card_mod:
  style: |
    ha-card {
      font-size: 1.5em;  # Increase or decrease this value
    }
```

### Changing Colors

The enhanced version uses gradient backgrounds. Modify these in the YAML:

```yaml
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Popular gradient combinations:
- Blue: `#4facfe 0%, #00f2fe 100%`
- Green: `#43e97b 0%, #38f9d7 100%`
- Orange: `#fa709a 0%, #fee140 100%`
- Purple: `#667eea 0%, #764ba2 100%`

### Adding/Removing Sensors

To add or remove sensors from the dashboard:

1. Find the relevant card section in the YAML
2. Add or remove entity entries:

```yaml
entities:
  - entity: sensor.ski_bromont_new_sensor
    name: Display Name
    icon: mdi:icon-name
```

**Note:** All sensor entity IDs are now prefixed with `ski_bromont_` (e.g., `sensor.ski_bromont_status`, `sensor.ski_bromont_snow_24h`).

## 📊 Dashboard Layout

### Enhanced Version Layout:
```
┌─────────────────────────────────────────┐
│     BROMONT MOUNTAIN - STATUS BANNER    │
├──────────────────┬──────────────────────┤
│  Snow Stats      │  Weather Forecast    │
│  Day Operations  │  Terrain Status      │
│  Night Ops       │  Terrain Grid        │
└──────────────────┴──────────────────────┘
│         Last Updated Footer             │
└─────────────────────────────────────────┘
```

### Simple Version Layout:
```
┌─────────────────────────────────────────┐
│          BROMONT MOUNTAIN HEADER        │
├──────────────────┬──────────────────────┤
│  Fresh Snow      │  Weather Forecast    │
│  Base Conditions │  Terrain Status      │
│  Day Operations  │  Terrain Quick View  │
│  Night Ops       │                      │
└──────────────────┴──────────────────────┘
│         Last Updated Footer             │
└─────────────────────────────────────────┘
```

## 🔧 Troubleshooting

### Weather Widget Shows "Unknown"

1. Verify your weather integration is configured
2. Check the entity name matches in the YAML
3. Ensure the weather integration is updating (check Developer Tools → States)

### Custom Cards Not Loading (Enhanced Version)

1. Verify all custom cards are installed via HACS
2. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
3. Check browser console for errors (F12)
4. Restart Home Assistant

### Sensors Show "Unavailable"

1. Verify the Bromont integration is configured and running
2. Check integration logs: **Settings** → **System** → **Logs**
3. Ensure internet connectivity to Ski Bromont website
4. Try reloading the integration

### Dashboard Not Appearing in Sidebar

1. Verify `configuration.yaml` has the lovelace configuration
2. Ensure the YAML file is in the correct directory
3. Check for YAML syntax errors
4. Restart Home Assistant

### Text Too Small/Large on TV

Adjust the base font size in the card_mod sections:
- Too small: Increase from `1.3em` to `1.8em` or `2em`
- Too large: Decrease from `1.3em` to `1em` or `0.8em`

## 📝 Additional Features

### Auto-Refresh

The dashboard automatically refreshes when sensor data updates. The Bromont integration updates based on your configured interval (default: 15 minutes).

### Mobile Responsive

Both dashboards work on mobile devices, though they're optimized for large TV displays.

### Dark/Light Theme

The dashboards respect your Home Assistant theme settings. For best TV viewing:
- Use a dark theme for reduced eye strain
- Recommended: "Backend-selected" theme

## 🆕 Entity ID Changes

All sensors are now prefixed with `ski_bromont_` for better organization:

- `sensor.ski_bromont_status` - Mountain status
- `sensor.ski_bromont_snow_24h` - 24h snow accumulation
- `sensor.ski_bromont_trails_day` - Day trails open
- `sensor.ski_bromont_lifts_day` - Day lifts open
- And all other sensors follow the same pattern

## 🤝 Contributing

Feel free to customize these dashboards for your needs! Share your improvements with the community.

## 📄 License

These dashboard configurations are provided as-is for use with the Bromont Mountain Conditions integration.

## 🔗 Related Links

- [Bromont Integration Repository](https://github.com/zopanix/ha-bromont-conditions)
- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [Lovelace Dashboard Documentation](https://www.home-assistant.io/lovelace/)
- [HACS Documentation](https://hacs.xyz/)

---

**Enjoy your Bromont Mountain dashboard! 🎿⛷️**