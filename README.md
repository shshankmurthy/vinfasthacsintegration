This repository is a fork of [https://github.com/vinfastownersorg-cyber/vinfastowners](https://github.com/vinfastownersorg-cyber/vinfastowners) and has been made compatible with HACS (Home Assistant Community Store) for easier installation and management. You can add this repository to HACS as a custom repository.

# VinFast Owners Community Resources

Open source tools, integrations, and resources for VinFast EV owners.

## Projects

### [VinFast Wall Panel Dashboard](example_config/dashboards/wall-panel/)
Beautiful glassmorphism-style dashboard for Nest Hub and tablet displays:
- Real-time battery, range, and charging status
- Live vehicle status (lock, plug, doors, gear)
- Multi-vehicle support (1-4 VinFasts)
- Unified map showing all vehicle locations
- Telemetry update status with manual refresh
- Optimized for Google Nest Hub 7"/10" displays

**[View Wall Panel Setup Guide](example_config/dashboards/wall-panel/README.md)**

### [VinFast Home Assistant Integration](custom_components/vinfast/)
Custom integration for VinFast Connected Car:
- Vehicle telemetry (battery, range, odometer, tire pressure)
- Location tracking with GPS
- Charging status and charge limit
- Door, trunk, hood, and window status
- Temperature (inside/outside)
- Region support (US, Europe, Vietnam)

### [OCPP Charger Integration](example_config/ocpp-setup/)
For VinFast owners with OCPP-compatible chargers:
- Real-time charger monitoring dashboard
- Charging cost tracking (session, daily, weekly, monthly)
- Gas savings calculator comparing EV vs gas costs
- Auto-start charging automation
- Voice announcements for charging events

[View Home Assistant Setup Guide](example_config/README.md)

## Contributing

Pull requests welcome! Please test your changes before submitting.

## Community

This repository is maintained by the VinFast Owners community.

## License

GPL-3.0 License - See [LICENSE](LICENSE) for details.
