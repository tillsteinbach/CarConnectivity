# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- No unreleased changes so far

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

[unreleased]: https://github.com/tillsteinbach/CarConnectivity/compare/v0.8...HEAD
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
