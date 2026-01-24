# CarConnectivity General Config Options
The configuration for CarConnectivity is a .json file.
## General format
The general format is a `carConnectivity` section, followed by a list of connectors and plugins.
In the `carConnectivity` section you can set the global `log_level`.
Each connector or plugin needs a `type` attribute and a `config` section.
The `type` and config options specific to your connector or plugin can be found on their respective project page.
```json
{
    "carConnectivity": {
        "log_level": "error", // set the global log level, you can set individual log levels in the connectors and plugins
        "connectors": [
            {
                "type": "skoda", // Definition for a MySkoda account
                "config": {
                    "interval": 600, // Interval in which the server is checked in seconds
                    "username": "test@test.de", // Username of your MySkoda Account
                    "password": "testpassword123" // Password of your MySkoda Account
                }
            },
            {
                "type": "volkswagen", // Definition for a Volkswagen account
                "config": {
                    "interval": 300, // Interval in which the server is checked in seconds
                    "username": "test@test.de", // Username of your Volkswagen Account
                    "password": "testpassword123" // Username of your Volkswagen Account
                }
            }
        ],
        "plugins": [
            {
                "type": "database", // Minimal definition for the Database Connection
                "config": {
                    "db_url": "sqlite:///carconnectivity.db" // Database URL to connect to the database
                }
            }
        ]
    }
}
```
### General Options
These are the valid options for the general configuration
```json
{
    "carConnectivity": {
        "log_level": "info",
        "initialization": { // The initialization section allows to predefine data that is not supplied by connectors. Supplying this data can improve user experience by having additional data available. If the connectors provide this data, it will override the predefined data.
            "garage": {
                "TMBLJ9NY8SF008152": { // One entry per VIN
                    "drives": {
                        "primary": {
                            "range_wltp": {"val": 550, "uni": "km"}, //Example to provide WLTP range (can be with or without unit)
                            "range_wltp": 550, //Example to provide WLTP range without unit (assumed to be in km)
                            "battery": {
                                "total_capacity": 82.0, // Example to provide total battery capacity in kWh
                                "available_capacity": 77.0 // Example to provide available battery capacity in kWh
                            }
                        }
                    }
                },
                "WVWZZZ3CZHE123456": { // Example for a second VIN (e.g. a hybrid vehicle)
                    "drives": {
                        "primary": {
                            "range_wltp": 450,
                            "fuel_tank": {
                                "available_capacity": 55.0
                            }
                        },
                        "secondary": {
                            "range_wltp": 52,
                            "battery": {
                                "total_capacity": 13.0,
                                "available_capacity": 10.0
                            }
                        }
                    }
            }
        },
        "geofences": [ // The geofences section allows to predefine geofences for location based services. Configure a list of geofences here.
            {
                "name": "Home", // Name of the geofence location
                "latitude": 53.625193, // Latitude of the geofence center
                "longitude": 10.100695, // Longitude of the geofence center
                "radius": 40, // Radius of the geofence in meters
                "location": { // Optional: Predefined location data for this geofence
                    "display_name": "Home", // Optional: Full display name for the location
                    "house_number": "1", // House number of the location
                    "road": "Spreeweg", // Road of the location
                    "neighbourhood": "Regierungsviertel", // Neighbourhood of the location
                    "city": "Berlin", // City of the location
                    "postcode": "10557", // Postal code of the location
                    "state": "Berlin", // State of the location
                    "country": "Deutschland" // Country of the location
                },
                "charging_station": { // Optional: Predefined charging station data for this geofence
                    "name": "Home Wallbox", // Name of the charging station
                    "operator_id": "myhome", // Operator ID of the charging station
                    "operator_name": "Schloss Bellevue", // Operator name of the charging station
                    "address": "Spreeweg 1, 10557 Berlin", // Address of the charging station
                    "max_power": 11.0, // Maximum power of the charging station in kW
                    "num_spots": 1 // Number of charging spots at the charging station
                }
            },
            { // Example for a second geofence
                "name": "Work",
                "latitude": 53.543680, 
                "longitude": 10.024038,
                "radius": 200,
                "location": {
                    "display_name": "Reichstag",
                    "house_number": "1",
                    "road": "Platz der Republik",
                    "neighbourhood": "Regierungsviertel",
                    "city": "Berlin",
                    "postcode": "11011",
                    "state": "Berlin",
                    "country": "Deutschland"
                },
                "charging_station": {
                    "name": "Reichstagsgebäude",
                    "operator_id": "bundestag",
                    "operator_name": "Deutscher Bundestag",
                    "address": "Platz der Republik 1, 11011 Berlin",
                    "max_power": 300.0,
                    "num_spots": 10
                }
            }
        ],
        "connectors": [],
        "plugins": []
}
```

### Connector Options
Valid Options for connectors can be found here:
* [CarConnectivity-connector-skoda Config Options](https://github.com/tillsteinbach/CarConnectivity-connector-skoda/tree/main/doc/Config.md)
* [CarConnectivity-connector-volkswagen Config Options](https://github.com/tillsteinbach/CarConnectivity-connector-volkswagen/tree/main/doc/Config.md)
* [CarConnectivity-connector-seatcupra Config Options](https://github.com/tillsteinbach/CarConnectivity-connector-seatcupra/tree/main/doc/Config.md)
* [CarConnectivity-connector-tronity Config Options](https://github.com/tillsteinbach/CarConnectivity-connector-tronity/tree/main/doc/Config.md)
