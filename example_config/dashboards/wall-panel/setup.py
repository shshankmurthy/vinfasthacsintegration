#!/usr/bin/env python3
"""
VinFast Wall Panel Dashboard Setup Script
Interactively configures entity IDs for your Home Assistant setup.
Supports multiple VinFast vehicles on the same dashboard.

Usage:
    python3 setup.py

This will create a configured version of the dashboard ready to paste into Home Assistant.
"""

import re
import os
import sys
import json

# Car card template - will be duplicated for each vehicle
CAR_CARD_TEMPLATE = '''      # ===== {vehicle_name} =====
      - type: custom:button-card
        view_layout:
          grid-area: {grid_area}
        entity: {battery_sensor}
        show_name: false
        show_icon: false
        show_state: false
        tap_action:
          action: navigate
          navigation_path: /wall-panel/cameras
        styles:
          card:
            - background: transparent
            - box-shadow: none
            - border: none
            - padding: 0
            - cursor: pointer
          custom_fields:
            content:
              - width: 100%
        custom_fields:
          content: |
            [[[
              // Battery and range
              const batt = Math.round(parseFloat(entity.state));
              const range = Math.round(parseFloat(states['{range_sensor}']?.state)) || 0;
              const chargeLimit = Math.round(parseFloat(states['{charge_limit_sensor}']?.state)) || 90;

              // Charging status
              const isCharging = states['{charging_binary}']?.state === 'on';
              const chargingStatus = states['{charging_status_sensor}']?.state || 'Unknown';
              const timeToFull = parseFloat(states['{time_to_full_sensor}']?.state) || 0;
              const chargingPower = states['{charging_power_sensor}']?.state;

              // Temperatures
              const insideTemp = Math.round(parseFloat(states['{inside_temp_sensor}']?.state)) || '--';
              const outsideTemp = Math.round(parseFloat(states['{outside_temp_sensor}']?.state)) || '--';

              // Vehicle status
              const isLocked = states['{locked_binary}']?.state === 'off'; // off means locked
              const isPluggedIn = states['{plug_binary}']?.state === 'on';
              const isIgnitionOn = states['{power_binary}']?.state === 'on';
              const gear = states['{gear_sensor}']?.state || 'P';
              const odometer = Math.round(parseFloat(states['{odometer_sensor}']?.state)) || 0;

              // Door/window status
              const doorsOpen = states['{door_binary}']?.state === 'on';
              const windowsOpen = states['{window_binary}']?.state === 'on';
              const trunkOpen = states['{trunk_binary}']?.state === 'on';
              const hoodOpen = states['{hood_binary}']?.state === 'on';

              // Location
              const location = states['{location_tracker}']?.state || 'unknown';
              const locationText = location === 'home' ? 'Home' : (location === 'not_home' ? 'Away' : location);

              // Battery color
              const getBattColor = (pct) => {{
                if (pct < 20) return '#f44336';
                if (pct < 40) return '#FFC107';
                return '#4CAF50';
              }};
              const battColor = getBattColor(batt);

              // Tire pressures (FL, FR, RL, RR)
              const fl = parseFloat(states['{tire_fl_sensor}']?.state) || 0;
              const fr = parseFloat(states['{tire_fr_sensor}']?.state) || 0;
              const rl = parseFloat(states['{tire_rl_sensor}']?.state) || 0;
              const rr = parseFloat(states['{tire_rr_sensor}']?.state) || 0;

              // Pressure color (normal 35-42 PSI for VF8)
              const getPressureColor = (psi) => {{
                if (psi < 32 || psi > 45) return '#f44336';
                if (psi < 35 || psi > 42) return '#FFC107';
                return '#4CAF50';
              }};

              // Charging time display
              const formatChargingTime = (mins) => {{
                if (mins <= 0) return '';
                const h = Math.floor(mins / 60);
                const m = Math.round(mins % 60);
                return h > 0 ? `${{h}}h ${{m}}m` : `${{m}}m`;
              }};

              return `
                <div style="padding: 0 8px;">
                  <div style="font-size: clamp(12px, 2vw, 16px); font-weight: 600; color: rgba(255,255,255,0.9); margin-bottom: 8px; text-align: center;">{vehicle_name}</div>
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: clamp(4px, 1vw, 8px);">
                    <div style="position: relative;">
                      <img src="{vehicle_image}" style="width: clamp(100px, 20vw, 180px); height: auto; filter: drop-shadow(0 10px 30px rgba(0,0,0,0.6));">
                      ${{isCharging ? '<div style="position: absolute; top: 5px; right: 5px; animation: pulse 1.5s ease-in-out infinite;"><ha-icon icon="mdi:lightning-bolt" style="--mdc-icon-size: 20px; color: #4CAF50; filter: drop-shadow(0 0 8px rgba(76,175,80,0.8));"></ha-icon></div>' : ''}}
                    </div>
                    <div style="text-align: right; padding-top: 4px;">
                      <div style="font-size: clamp(24px, 5vw, 40px); font-weight: 300; color: ${{battColor}}; line-height: 1;">${{batt}}%</div>
                      <div style="font-size: clamp(11px, 2vw, 14px); color: rgba(255,255,255,0.6);">${{range}} mi</div>
                      <div style="display: flex; justify-content: flex-end; align-items: center; gap: 4px; margin-top: 4px;">
                        <ha-icon icon="mdi:thermometer" style="--mdc-icon-size: 12px; color: #64B5F6;"></ha-icon>
                        <span style="font-size: 10px; color: rgba(255,255,255,0.6);">${{insideTemp}}°</span>
                        <span style="font-size: 10px; color: rgba(255,255,255,0.6);">${{outsideTemp}}°</span>
                      </div>
                    </div>
                  </div>

                  <div style="background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 10px;">
                    <!-- Battery bar -->
                    <div style="position: relative; width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; margin-bottom: 8px;">
                      <div style="position: absolute; left: 0; top: 0; height: 100%; width: ${{batt}}%; background: ${{battColor}}; border-radius: 4px; ${{isCharging ? 'animation: charging-pulse 2s ease-in-out infinite;' : ''}}"></div>
                      <div style="position: absolute; left: ${{chargeLimit}}%; top: -2px; bottom: -2px; width: 2px; background: rgba(255,255,255,0.6);"></div>
                    </div>

                    <!-- Status row -->
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: rgba(255,255,255,0.7); margin-bottom: 8px;">
                      <div style="display: flex; align-items: center; gap: 4px;">
                        <ha-icon icon="${{location === 'home' ? 'mdi:home' : 'mdi:map-marker'}}" style="--mdc-icon-size: 12px; color: ${{location === 'home' ? '#4CAF50' : '#64B5F6'}};"></ha-icon>
                        <span>${{locationText}}</span>
                      </div>
                      <span>${{odometer.toLocaleString()}} mi</span>
                    </div>

                    <!-- Status icons -->
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px;">
                      <div style="text-align: center; padding: 6px 2px; background: ${{isIgnitionOn ? 'rgba(76,175,80,0.2)' : 'rgba(255,255,255,0.05)'}}; border-radius: 6px;">
                        <div style="font-size: 14px; font-weight: 600; color: ${{isIgnitionOn ? '#4CAF50' : 'rgba(255,255,255,0.7)'}};">${{gear}}</div>
                      </div>
                      <div style="text-align: center; padding: 6px 2px; background: ${{isLocked ? 'rgba(76,175,80,0.2)' : 'rgba(255,193,7,0.2)'}}; border-radius: 6px;">
                        <ha-icon icon="${{isLocked ? 'mdi:lock' : 'mdi:lock-open'}}" style="--mdc-icon-size: 16px; color: ${{isLocked ? '#4CAF50' : '#FFC107'}};"></ha-icon>
                      </div>
                      <div style="text-align: center; padding: 6px 2px; background: ${{isPluggedIn ? 'rgba(76,175,80,0.2)' : 'rgba(255,255,255,0.05)'}}; border-radius: 6px;">
                        <ha-icon icon="${{isPluggedIn ? 'mdi:ev-plug-type1' : 'mdi:power-plug-off'}}" style="--mdc-icon-size: 16px; color: ${{isPluggedIn ? '#4CAF50' : 'rgba(255,255,255,0.5)'}};"></ha-icon>
                      </div>
                      <div style="text-align: center; padding: 6px 2px; background: ${{(doorsOpen || windowsOpen) ? 'rgba(255,193,7,0.2)' : 'rgba(76,175,80,0.2)'}}; border-radius: 6px;">
                        <ha-icon icon="${{(doorsOpen || windowsOpen) ? 'mdi:car-door' : 'mdi:shield-check'}}" style="--mdc-icon-size: 16px; color: ${{(doorsOpen || windowsOpen) ? '#FFC107' : '#4CAF50'}};"></ha-icon>
                      </div>
                    </div>
                  </div>
                </div>
              `;
            ]]]
        extra_styles: |
          @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.7; transform: scale(1.1); }}
          }}
          @keyframes charging-pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
          }}
'''

# Grid layouts for different numbers of vehicles
GRID_LAYOUTS = {
    1: {
        "columns": "minmax(200px, 260px) 1fr 1fr minmax(160px, 200px)",
        "rows": "1fr auto",
        "areas": '"timeweather map car1 status"\n        "energy security security battery"',
        "car_areas": ["car1"]
    },
    2: {
        "columns": "minmax(180px, 220px) 1fr 1fr minmax(140px, 180px)",
        "rows": "1fr auto",
        "areas": '"timeweather car1 car2 status"\n        "energy map map battery"',
        "car_areas": ["car1", "car2"]
    },
    3: {
        "columns": "minmax(160px, 200px) 1fr 1fr 1fr minmax(140px, 170px)",
        "rows": "1fr auto",
        "areas": '"timeweather car1 car2 car3 status"\n        "energy map map map battery"',
        "car_areas": ["car1", "car2", "car3"]
    },
    4: {
        "columns": "minmax(160px, 200px) 1fr 1fr 1fr 1fr",
        "rows": "1fr auto",
        "areas": '"timeweather car1 car2 car3 car4"\n        "energy map map map battery"',
        "car_areas": ["car1", "car2", "car3", "car4"]
    }
}

# Map card template for multiple vehicles
MAP_CARD_TEMPLATE = '''      # ===== ALL VEHICLES LOCATION MAP =====
      - type: map
        view_layout:
          grid-area: map
          align-self: start
        entities:
{map_entities}
        dark_mode: true
        default_zoom: 14
        hours_to_show: 0
        tap_action:
          action: more-info
        card_mod:
          style: |
            ha-card {{
              background: rgba(255,255,255,0.05) !important;
              backdrop-filter: blur(20px);
              -webkit-backdrop-filter: blur(20px);
              border: 1px solid rgba(255,255,255,0.1);
              border-radius: 16px;
              box-shadow: 0 8px 32px rgba(0,0,0,0.3);
              overflow: hidden;
              height: clamp(200px, 40vw, 350px) !important;
              cursor: pointer;
            }}
            #map, .leaflet-container {{
              height: 100% !important;
              min-height: 100% !important;
            }}
'''

# Vehicle entity fields
VEHICLE_FIELDS = [
    ("name", "Vehicle name/nickname", "My VF8", True),
    ("image", "Vehicle image path", "/local/vinfast/vf8.png", True),
    ("battery_sensor", "Battery level sensor", "sensor.vf8_battery", True),
    ("range_sensor", "Range sensor", "sensor.vf8_range", True),
    ("charge_limit_sensor", "Charge limit sensor", "sensor.vf8_charge_limit", False),
    ("charging_status_sensor", "Charging status sensor", "sensor.vf8_charging_status", False),
    ("time_to_full_sensor", "Time to full charge sensor", "sensor.vf8_time_to_full", False),
    ("charging_power_sensor", "Charging power sensor", "sensor.vf8_charging_power", False),
    ("inside_temp_sensor", "Inside temperature sensor", "sensor.vf8_temperature_2", False),
    ("outside_temp_sensor", "Outside temperature sensor", "sensor.vf8_temperature", False),
    ("gear_sensor", "Gear sensor", "sensor.vf8_none", False),
    ("odometer_sensor", "Odometer sensor", "sensor.vf8_odometer", False),
    ("tire_fl_sensor", "Tire pressure FL sensor", "sensor.vf8_pressure", False),
    ("tire_fr_sensor", "Tire pressure FR sensor", "sensor.vf8_pressure_2", False),
    ("tire_rl_sensor", "Tire pressure RL sensor", "sensor.vf8_pressure_3", False),
    ("tire_rr_sensor", "Tire pressure RR sensor", "sensor.vf8_pressure_4", False),
    ("charging_binary", "Is charging binary sensor", "binary_sensor.vf8_charging", False),
    ("locked_binary", "Lock status binary sensor", "binary_sensor.vf8_locked", False),
    ("plug_binary", "Plug connected binary sensor", "binary_sensor.vf8_plug", False),
    ("power_binary", "Ignition/power binary sensor", "binary_sensor.vf8_power", False),
    ("door_binary", "Door open binary sensor", "binary_sensor.vf8_door", False),
    ("window_binary", "Window open binary sensor", "binary_sensor.vf8_window", False),
    ("trunk_binary", "Trunk open binary sensor", "binary_sensor.vf8_opening", False),
    ("hood_binary", "Hood open binary sensor", "binary_sensor.vf8_opening_2", False),
    ("location_tracker", "Location device tracker", "device_tracker.vf8_location", True),
]

# Other dashboard entities (non-vehicle)
OTHER_ENTITIES = {
    "weather.forecast_home": ("Weather entity", "weather.home", True),
    "alarm_control_panel.home_alarm": ("Alarm panel (or 'skip')", "alarm_control_panel.home", False),
    "binary_sensor.garage_door": ("Garage door sensor", "binary_sensor.garage", False),
    "person.person_1": ("Person 1 entity", "person.john", False),
    "person.person_2": ("Person 2 entity (or 'skip')", "person.jane", False),
    "device_tracker.person_1": ("Person 1 tracker", "device_tracker.john", False),
    "device_tracker.person_2": ("Person 2 tracker", "device_tracker.jane", False),
    "sensor.phone_1_battery_level": ("Phone 1 battery", "sensor.john_phone_battery", False),
    "sensor.phone_2_battery_level": ("Phone 2 battery", "sensor.jane_phone_battery", False),
    "sensor.camera_1_battery": ("Camera 1 battery (or 'skip')", "sensor.front_cam_battery", False),
    "sensor.camera_2_battery": ("Camera 2 battery", "sensor.back_cam_battery", False),
    "sensor.camera_3_battery": ("Camera 3 battery", "sensor.garage_cam_battery", False),
    "sensor.camera_4_battery": ("Camera 4 battery", "sensor.driveway_cam_battery", False),
    "sensor.ev_savings_today": ("EV savings today (or 'skip')", "sensor.ev_daily_savings", False),
    "sensor.ev_savings_month": ("EV savings month", "sensor.ev_monthly_savings", False),
    "sensor.ev_savings_percent": ("EV savings percent", "sensor.ev_savings_pct", False),
    "Person 1": ("Person 1 display name", "John", False),
    "Person 2": ("Person 2 display name", "Jane", False),
    "/local/vinfast/vf_bg.png": ("Background image path", "/local/backgrounds/ev.png", True),
}


def print_header():
    print("\n" + "=" * 60)
    print("  VinFast Wall Panel Dashboard Setup")
    print("  Multi-Vehicle Support")
    print("=" * 60)
    print("\nThis script configures the dashboard for your Home Assistant.")
    print("Supports 1-4 VinFast vehicles on a single dashboard.")
    print("\nTips:")
    print("  - Find entities: Settings > Devices & Services > VinFast")
    print("  - Press Enter to accept default or skip optional fields")
    print("  - Type 'quit' at any time to exit")
    print()


def get_input(prompt, example, required=False, default=None):
    """Get user input with example and validation."""
    req = " *" if required else ""
    if default:
        prompt_text = f"  {prompt}{req}\n    Example: {example}\n    Default: {default}\n    > "
    else:
        prompt_text = f"  {prompt}{req}\n    Example: {example}\n    > "

    while True:
        value = input(prompt_text).strip()
        if value.lower() == 'quit':
            print("\nExiting without saving.")
            sys.exit(0)
        if value.lower() == 'skip':
            return None
        if not value:
            if required and not default:
                print("    This field is required.\n")
                continue
            return default
        return value


def collect_vehicle_info(vehicle_num, prefix=None):
    """Collect all entity info for a single vehicle."""
    print(f"\n--- Vehicle {vehicle_num} Configuration ---\n")

    vehicle = {}

    for field, prompt, example, required in VEHICLE_FIELDS:
        # Apply prefix to example if provided
        if prefix and field != "name" and field != "image":
            example = example.replace("vf8", prefix)
            default = example if not required else None
        else:
            default = None

        if field == "name":
            default = f"VinFast {vehicle_num}"
        elif field == "image":
            default = "/local/vinfast/vf8.png"

        value = get_input(prompt, example, required, default)
        vehicle[field] = value if value else example

    return vehicle


def generate_map_card(vehicles):
    """Generate a map card with all vehicle locations."""
    map_entities = ""
    for vehicle in vehicles:
        tracker = vehicle.get("location_tracker", "device_tracker.unavailable")
        name = vehicle.get("name", "Vehicle")
        map_entities += f"          - entity: {tracker}\n            name: {name}\n"
    return MAP_CARD_TEMPLATE.format(map_entities=map_entities)


def generate_car_card(vehicle, grid_area):
    """Generate a car card YAML for a single vehicle."""
    return CAR_CARD_TEMPLATE.format(
        vehicle_name=vehicle["name"],
        grid_area=grid_area,
        vehicle_image=vehicle["image"],
        battery_sensor=vehicle["battery_sensor"],
        range_sensor=vehicle["range_sensor"],
        charge_limit_sensor=vehicle.get("charge_limit_sensor", "sensor.unavailable"),
        charging_status_sensor=vehicle.get("charging_status_sensor", "sensor.unavailable"),
        time_to_full_sensor=vehicle.get("time_to_full_sensor", "sensor.unavailable"),
        charging_power_sensor=vehicle.get("charging_power_sensor", "sensor.unavailable"),
        inside_temp_sensor=vehicle.get("inside_temp_sensor", "sensor.unavailable"),
        outside_temp_sensor=vehicle.get("outside_temp_sensor", "sensor.unavailable"),
        gear_sensor=vehicle.get("gear_sensor", "sensor.unavailable"),
        odometer_sensor=vehicle.get("odometer_sensor", "sensor.unavailable"),
        tire_fl_sensor=vehicle.get("tire_fl_sensor", "sensor.unavailable"),
        tire_fr_sensor=vehicle.get("tire_fr_sensor", "sensor.unavailable"),
        tire_rl_sensor=vehicle.get("tire_rl_sensor", "sensor.unavailable"),
        tire_rr_sensor=vehicle.get("tire_rr_sensor", "sensor.unavailable"),
        charging_binary=vehicle.get("charging_binary", "binary_sensor.unavailable"),
        locked_binary=vehicle.get("locked_binary", "binary_sensor.unavailable"),
        plug_binary=vehicle.get("plug_binary", "binary_sensor.unavailable"),
        power_binary=vehicle.get("power_binary", "binary_sensor.unavailable"),
        door_binary=vehicle.get("door_binary", "binary_sensor.unavailable"),
        window_binary=vehicle.get("window_binary", "binary_sensor.unavailable"),
        trunk_binary=vehicle.get("trunk_binary", "binary_sensor.unavailable"),
        hood_binary=vehicle.get("hood_binary", "binary_sensor.unavailable"),
        location_tracker=vehicle.get("location_tracker", "device_tracker.unavailable"),
    )


def main():
    print_header()

    # Get number of vehicles
    while True:
        num_input = input("How many VinFast vehicles do you have? (1-4): ").strip()
        if num_input.lower() == 'quit':
            sys.exit(0)
        try:
            num_vehicles = int(num_input)
            if 1 <= num_vehicles <= 4:
                break
            print("  Please enter a number between 1 and 4.\n")
        except ValueError:
            print("  Please enter a valid number.\n")

    # Ask for common prefix
    print("\n--- Quick Setup ---")
    print("If your VinFast entities share a common prefix, enter it to auto-fill.")
    print("Example: If battery is 'sensor.myvf8_battery', prefix is 'myvf8'")
    prefix = input("Entity prefix (or Enter to skip): ").strip() or None

    # Collect vehicle info
    vehicles = []
    for i in range(1, num_vehicles + 1):
        vehicle = collect_vehicle_info(i, prefix)
        vehicles.append(vehicle)

    # Collect other entities
    print("\n--- Other Dashboard Entities ---\n")
    other_replacements = {}
    skip_sections = set()

    for entity, (prompt, example, required) in OTHER_ENTITIES.items():
        value = get_input(prompt, example, required)
        if value is None:
            if "alarm" in entity:
                skip_sections.add("security")
            elif "ev_savings" in entity:
                skip_sections.add("ev_savings")
        else:
            other_replacements[entity] = value

    # Read template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_file = os.path.join(script_dir, "vinfast-wall-panel.yaml")

    if not os.path.exists(template_file):
        print(f"\nError: Template file not found: {template_file}")
        sys.exit(1)

    with open(template_file, 'r') as f:
        template = f.read()

    # Generate output
    print("\n--- Generating Dashboard ---\n")

    # Get layout for this number of vehicles
    layout = GRID_LAYOUTS[num_vehicles]

    # Update grid layout in template
    output = template

    # Replace grid template columns
    output = re.sub(
        r'grid-template-columns: [^\n]+',
        f'grid-template-columns: {layout["columns"]}',
        output,
        count=1
    )

    # Replace grid template areas
    output = re.sub(
        r'grid-template-areas: \|[^|]+\|',
        f'grid-template-areas: |\n        {layout["areas"]}',
        output,
        count=1
    )

    # Find and replace the car section
    # Remove the original car card (between "EV CAR SECTION" and "EV SAVINGS SECTION")
    car_section_start = output.find("# ===== EV CAR SECTION")
    car_section_end = output.find("# ===== EV SAVINGS SECTION")

    if car_section_start != -1 and car_section_end != -1:
        # Generate all car cards
        car_cards = ""
        for i, vehicle in enumerate(vehicles):
            grid_area = layout["car_areas"][i]
            car_cards += generate_car_card(vehicle, grid_area) + "\n"

        # Replace car section
        output = output[:car_section_start] + car_cards + "\n      " + output[car_section_end:]

    # Replace the map section with multi-vehicle map
    map_section_start = output.find("# ===== VF8 LOCATION MAP =====")
    if map_section_start == -1:
        map_section_start = output.find("# ===== ALL VEHICLES LOCATION MAP =====")
    map_section_end = output.find("# ===== PARKED CAMERAS VIEW =====")

    if map_section_start != -1 and map_section_end != -1:
        # Generate multi-vehicle map card
        map_card = generate_map_card(vehicles)
        output = output[:map_section_start] + map_card + "\n\n  " + output[map_section_end:]

    # Apply other entity replacements
    for old, new in other_replacements.items():
        output = output.replace(old, new)

    # Write output
    output_file = os.path.join(script_dir, "my-vinfast-wall-panel.yaml")
    with open(output_file, 'w') as f:
        f.write(output)

    print(f"Dashboard saved to: {output_file}")
    print(f"  - {num_vehicles} vehicle(s) configured")
    print(f"  - Layout adjusted for multi-vehicle display")

    print("\n--- Next Steps ---")
    print("1. Go to Home Assistant > Settings > Dashboards")
    print("2. Create new dashboard 'Wall Panel' with URL 'wall-panel'")
    print("3. Edit Dashboard > Raw Configuration Editor")
    print(f"4. Paste contents of: my-vinfast-wall-panel.yaml")
    print("5. Save and refresh!")

    # Save config for reference
    config = {
        "num_vehicles": num_vehicles,
        "vehicles": vehicles,
        "other_entities": other_replacements
    }
    config_file = os.path.join(script_dir, "my-config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"\nConfiguration saved to: {config_file}")
    print("(You can re-run setup.py to modify settings)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting.")
        sys.exit(0)
