# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- No unreleased changes so far

## [0.11.6] - 2026-01-23
### Changed
- Internal callbacks now use higher pririty to ensure they are called before external ones
- BaseConnector now provides commands to allow for updating the session

## [0.11.5] - 2026-01-11
### Fixed
- Fixes a bug where when initialized with static entries, precision was not yet initialized when notificaln callbacks were called

## [0.11.4] - 2026-01-11
### Added
- Adds support for more flexible parameters for plugins and connectors and their UIs to allow better backwards compatibility in the future
- Support for storing measurement source in attributes to allow connectors to better deal with multi source attributes
- Support for generating dicts and json using locales and conversion of units

### Changed
- Don't fail on invalid locale in config, just log a warning and use system locale instead

## [0.11.3] - 2026-01-10
### Added
- Adds global locale option that can be inherited by plugins and connectors

## [0.11.2] - 2026-01-08
### Changed
- Locks now use timeout mechanism to avoid deadlocks in some situations

## [0.11.1] - 2026-01-04
### Fixed
- Updated version requirements for all connectors and plugins

## [0.11] - 2026-01-04
### Added
- Support for initializing attributes on startup form static entries in the configuration
- This version is adding experimental support for a [VWSFriend](http://github.com/tillsteinbach/vwsfriend) like user experience using [carconnectivity-plugin-database](http://github.com/tillsteinbach/carconnectivity-plugin-database) and [carconnectivity-grafana](http://github.com/tillsteinbach/carconnectivity-grafana)

Warning: This is a breaking change for all connectors and plugins. Only update to this version if you use a connector that has been updated to support this feature.

## [0.10] - 2025-12-31 Happy New Year!
### Added
- Check against NTP server for time synchronization
- Attributes for WLTP range, estimated range at 100% charge and estimated consumption
- Add fuel tank to combustion vehicles and adblue tank to diesel vehicles
- Add location object to vehicle position
- Add charging station object to charging information
- Infrastructure for managing services to fetch additional data (like location, etc.)
- Add service for fetching location data based on coordinates from OpenStreetMap
- Add service for fetching charging station data based on coordinates from OpenChargeMap 

## [0.9.2] - 2025-11-10
### Fixed
- Set default log levels correctly

## [0.9.1] - 2025-11-07
### Fixed
- Fixes a bug where optional features status messages were not shown correctly

## [0.9] - 2025-11-07
### Added
- Support for managing optional features in connectors and plugins

## [0.8.1] - 2025-11-02
### Changed
- Updated some dependencies

## [0.8] - 2025-07-27
### Added
- Adds convencience method to get combustion engine for combustion vehicles

## [0.7.2] - 2025-06-26
### Fixed
- Fixes a problem with robust time parsing under python 3.10 when fractional seconds were more than 6 digits long

## [0.7.1] - 2025-06-20
### Fixed
- Fixes bug that registers hooks several times, causing multiple calls to the servers (Thanks to @amne for the fix)

## [0.7] - 2025-04-17
### Added
- Support for pretty printing json
- All float attributes now support precision (with default)

### Changed
- Updated some dependencies
- Improved signal handling when terminating with SIGTERM and SIGINT

## [0.6] - 2025-04-02
### Fixed
- Bug when pillow was installed but ascii_magic not

### Added
- Support for running multiple instances of the same plugin or connector
- Example for start/stop charging
- Support for Lengths in meter and feet
- Support for raising multiple exceptions together (used for connectors)
- Added Open state AJAR (used with Volvos)
- Added support for altitude and heading attributes (used with Volvos)
- 'hide_vins' configuration option for connectors

### Changed
- Updated some dependencies
- Improved usability with commands

## [0.5] - 2025-03-20
### Added
- Support for window heating attributes
- Support for window heating command
### Changed
- More checks and robustness

## [0.4] - 2025-03-02
### Added
- Support for battery attributes
- Support for maintenance attributes
- Set hooks can now be early or late
- More functionallity for connection states
- Object trees can now be obtained as dict of json
- Added units for energy
- Added support for minimum, maximum and precision checks
- Added vehicle connection state
- Connectors now publish their health status

### Fixed
- Fixed types for some Enum attributes
- json now can contain null values
- Fixed charging object

## [0.3] - 2025-02-19
### Added
- Added support for images
- Added tags to attributes
- Added support for webui via carconnectivity-plugin-webui

## [0.2] - 2025-02-02
### Added
- Adds heater source attribute and default implementation of wake command

## [0.1] - 2025-01-25
Initial release, let's go and give this to the public to try out...

[unreleased]: https://github.com/tillsteinbach/CarConnectivity/compare/v0.11.5...HEAD
[0.11.5]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.11.5
[0.11.4]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.11.4
[0.11.3]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.11.3
[0.11.2]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.11.2
[0.11.1]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.11.1
[0.11]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.11
[0.10]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.10
[0.9.2]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.9.2
[0.9.1]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.9.1
[0.9]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.9
[0.8.1]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.8.1
[0.8]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.8
[0.7.2]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.7.2
[0.7.1]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.7.1
[0.7]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.7
[0.6]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.6
[0.5]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.5
[0.4]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.4
[0.3]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.3
[0.2]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.2
[0.1]: https://github.com/tillsteinbach/CarConnectivity/releases/tag/v0.1
