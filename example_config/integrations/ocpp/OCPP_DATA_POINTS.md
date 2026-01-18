# OCPP Data Points Reference for Home Assistant

This document lists all OCPP (Open Charge Point Protocol) data points available when using an OCPP-compatible EV charger with Home Assistant.

Based on testing with an **Autel MaxiChargerAC** connected via the Home Assistant OCPP integration.

## Charger Identity

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.charger_id` | string | Charger identifier name |
| `sensor.charger_vendor` | string | Manufacturer name |
| `sensor.charger_model` | string | Charger model |
| `sensor.charger_serial` | string | Serial number |
| `sensor.charger_version_firmware` | string | Firmware version(s) |
| `sensor.charger_features` | string | Supported OCPP features (CORE, FW, SMART, REM, AUTH, etc.) |

## Status Sensors

| Entity | Type | Possible Values | Description |
|--------|------|-----------------|-------------|
| `sensor.charger_status` | string | Available, Preparing, Charging, SuspendedEV, SuspendedEVSE, Finishing, Reserved, Unavailable, Faulted | Overall charger status |
| `sensor.charger_status_connector` | string | Same as above | Individual connector status |
| `sensor.charger_error_code` | string | NoError, ConnectorLockFailure, EVCommunicationError, GroundFailure, etc. | Current error code |
| `sensor.charger_error_code_connector` | string | Same as above | Connector-specific error |
| `sensor.charger_stop_reason` | string | EmergencyStop, EVDisconnected, HardReset, Local, Remote, etc. | Reason last session stopped |
| `sensor.charger_status_firmware` | string | unknown, Downloaded, Downloading, etc. | Firmware update status |

## Energy Metering

| Entity | Unit | Description |
|--------|------|-------------|
| `sensor.charger_energy_active_import_register` | kWh | Total lifetime energy imported (main meter) |
| `sensor.charger_energy_meter_start` | kWh | Meter reading at session start |
| `sensor.charger_energy_session` | kWh | Energy delivered in current/last session |
| `sensor.charger_energy_today` | kWh | Energy delivered today |
| `sensor.charger_energy_daily` | kWh | Alternative daily energy counter |
| `sensor.charger_energy_weekly` | kWh | Energy delivered this week |
| `sensor.charger_energy_monthly` | kWh | Energy delivered this month |

### Interval Metering (may be unavailable on some chargers)

| Entity | Unit | Description |
|--------|------|-------------|
| `sensor.charger_energy_active_import_interval` | kWh | Energy imported since last interval |
| `sensor.charger_energy_active_export_interval` | kWh | Energy exported since last interval (V2G) |
| `sensor.charger_energy_active_export_register` | kWh | Total lifetime energy exported (V2G) |
| `sensor.charger_energy_reactive_import_register` | kvarh | Reactive energy imported |
| `sensor.charger_energy_reactive_export_register` | kvarh | Reactive energy exported |
| `sensor.charger_energy_reactive_import_interval` | kvarh | Reactive import interval |
| `sensor.charger_energy_reactive_export_interval` | kvarh | Reactive export interval |

## Power & Electrical

| Entity | Unit | Description |
|--------|------|-------------|
| `sensor.charger_power_active_import` | kW | Current charging power |
| `sensor.charger_power_offered` | kW | Power offered to vehicle |
| `sensor.charger_current_import` | A | Current being drawn |
| `sensor.charger_current_export` | A | Current being exported (V2G) |
| `sensor.charger_voltage` | V | Line voltage |
| `number.charger_maximum_current` | A | Maximum current setting (adjustable) |

### Additional Electrical (may be unavailable on some chargers)

| Entity | Unit | Description |
|--------|------|-------------|
| `sensor.charger_power_active_export` | kW | Export power (V2G) |
| `sensor.charger_power_reactive_import` | var | Reactive power import |
| `sensor.charger_power_reactive_export` | var | Reactive power export |
| `sensor.charger_power_factor` | - | Power factor (0-1) |
| `sensor.charger_frequency` | Hz | AC frequency |

## Session Information

| Entity | Unit | Description |
|--------|------|-------------|
| `sensor.charger_time_session` | min | Duration of current/last session |
| `sensor.charger_transaction_id` | - | Unique transaction identifier |
| `sensor.charger_id_tag` | string | RFID/authentication tag used |

## Vehicle Information (if supported)

| Entity | Unit | Description |
|--------|------|-------------|
| `sensor.charger_soc` | % | Vehicle State of Charge (requires vehicle support) |
| `sensor.charger_temperature` | °C/°F | Charger/connector temperature |
| `sensor.charger_rpm` | Hz | Fan RPM (if applicable) |

## Connection Health

| Entity | Unit | Description |
|--------|------|-------------|
| `sensor.charger_heartbeat` | timestamp | Last heartbeat received |
| `sensor.charger_latency_ping` | ms | Ping latency to charger |
| `sensor.charger_latency_pong` | ms | Pong response latency |
| `sensor.charger_reconnects` | count | Number of reconnections |
| `sensor.charger_connectors` | count | Number of charge connectors |
| `sensor.charger_timestamp_config_response` | timestamp | Last config response |
| `sensor.charger_timestamp_data_response` | timestamp | Last data response |
| `sensor.charger_timestamp_data_transfer` | timestamp | Last data transfer |

## Controls

| Entity | Type | Description |
|--------|------|-------------|
| `switch.charger_availability` | switch | Enable/disable charger |
| `switch.charger_charge_control` | switch | Start/stop charging session |
| `button.charger_reset` | button | Reset the charger |
| `button.charger_unlock` | button | Unlock the connector |
| `number.charger_maximum_current` | number | Set maximum charging current (amps) |

## Charger Compatibility Notes

### Autel MaxiChargerAC

**Working:**
- All identity sensors
- Status and error codes
- Energy metering (lifetime, session, daily, weekly, monthly)
- Power and current measurements
- Session tracking
- All controls

**Not Available:**
- SoC (State of Charge) - requires ISO 15118 vehicle support
- Temperature sensor
- Frequency measurement
- Power factor
- Reactive power measurements
- Export/V2G features

### Common Issues

1. **SoC unavailable**: Most Level 2 chargers cannot read vehicle SoC. This requires ISO 15118 communication which most vehicles don't support over AC charging.

2. **Temperature unavailable**: Not all chargers have temperature sensors exposed via OCPP.

3. **Reactive power unavailable**: Many residential chargers don't measure reactive power.

4. **Interval meters unavailable**: Some chargers only report register (cumulative) values, not interval values.

## Example Automations

### Notify when charging complete

```yaml
automation:
  - alias: "EV Charging Complete"
    trigger:
      - platform: state
        entity_id: sensor.charger_status_connector
        to: "Finishing"
    action:
      - service: notify.mobile_app
        data:
          title: "EV Charging Complete"
          message: "Charged {{ states('sensor.charger_energy_session') }} kWh"
```

### Track monthly energy costs

```yaml
sensor:
  - platform: template
    sensors:
      charger_monthly_cost:
        friendly_name: "Monthly Charging Cost"
        unit_of_measurement: "$"
        value_template: >
          {{ (states('sensor.charger_energy_monthly') | float * 0.12) | round(2) }}
```

### Limit charging current during peak hours

```yaml
automation:
  - alias: "Reduce Charging During Peak"
    trigger:
      - platform: time
        at: "16:00:00"
    condition:
      - condition: state
        entity_id: sensor.charger_status
        state: "Charging"
    action:
      - service: number.set_value
        target:
          entity_id: number.charger_maximum_current
        data:
          value: 8
```

## Resources

- [Home Assistant OCPP Integration](https://github.com/lbbrhzn/ocpp)
- [OCPP Protocol Specification](https://www.openchargealliance.org/protocols/ocpp-16/)
- [Home Assistant Community - OCPP](https://community.home-assistant.io/t/ocpp-integration/389600)

---

*Document based on real-world testing with Home Assistant OCPP integration*
