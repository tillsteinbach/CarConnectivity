

# CarConnectivity
[![GitHub sourcecode](https://img.shields.io/badge/Source-GitHub-green)](https://github.com/tillsteinbach/CarConnectivity/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/tillsteinbach/CarConnectivity)](https://github.com/tillsteinbach/CarConnectivity/releases/latest)
[![GitHub](https://img.shields.io/github/license/tillsteinbach/CarConnectivity)](https://github.com/tillsteinbach/CarConnectivity/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/tillsteinbach/CarConnectivity)](https://github.com/tillsteinbach/CarConnectivity/issues)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/carconnectivity?label=PyPI%20Downloads)](https://pypi.org/project/carconnectivity/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/carconnectivity)](https://pypi.org/project/carconnectivity/)
[![Donate at PayPal](https://img.shields.io/badge/Donate-PayPal-2997d8)](https://www.paypal.com/donate?hosted_button_id=2BVFF5GJ9SXAJ)
[![Sponsor at Github](https://img.shields.io/badge/Sponsor-GitHub-28a745)](https://github.com/sponsors/tillsteinbach)

## CarConnectivity will become the successor of [WeConnect-python](https://github.com/tillsteinbach/WeConnect-python) in 2025 with similar functionality but support for other brands beyond Volkswagen!

Python API to connect to various car services. If you are not a developer and ended up here you probably want to check out a project using this library (see below).

## Projects in which the library is used
- [CarConnectivity-cli](https://github.com/tillsteinbach/CarConnectivity-cli): A commandline interface to interact with your Vehicles
- [CarConnectivity-MQTT](https://github.com/tillsteinbach/CarConnectivity-plugin-mqtt): A MQTT Client that provides Vehicle data to the MQTT Broker of your choice (e.g. your home automation solution such as [ioBroker](https://www.iobroker.net), [FHEM](https://fhem.de) or [Home Assistant](https://www.home-assistant.io))

## Supported Car Brands
CarConenctivity uses a connector plugin architecture to enable access to the services of various brands. Currently known connector plugins are:

| Brand                            | Connector                                                                                                     |
|----------------------------------|---------------------------------------------------------------------------------------------------------------|
| Skoda                            | [CarConnectivity-connector-skoda](https://github.com/tillsteinbach/CarConnectivity-connector-skoda)           |
| Volkswagen                       | [CarConnectivity-connector-volkswagen](https://github.com/tillsteinbach/CarConnectivity-connector-volkswagen) |
| Seat/Cupra                       | [CarConnectivity-connector-seatcupra](https://github.com/tillsteinbach/CarConnectivity-connector-seatcupra)   |
| [Troniy](https://www.tronity.io) | [CarConnectivity-connector-tronity](https://github.com/tillsteinbach/CarConnectivity-connector-tronity)       |

If you know of a connector not listed here let me know and I will add it to the list.
If you are a python developer and willing to implement a connector for a brand not listed here, let me know and I try to support you as good as possible

## Supported Plugins
CarConenctivity uses a plugin architecture to enable connectivity to other services and protocols. Currently known plugins are:

| Service or Protocol              | Connector                                                                                         |
|----------------------------------|---------------------------------------------------------------------------------------------------|
| WebUI (easy to use webinterface) | [CarConnectivity-plugin-webui](https://github.com/tillsteinbach/CarConnectivity-plugin-webui)     |
| MQTT                             | [CarConnectivity-plugin-mqtt](https://github.com/tillsteinbach/CarConnectivity-plugin-mqtt)       |
| A Better Routeplanner (ABRP)     | [CarConnectivity-plugin-abrp](https://github.com/tillsteinbach/CarConnectivity-plugin-abrp)       |
| Apple Homekit                    | [CarConnectivity-plugin-homekit](https://github.com/tillsteinbach/CarConnectivity-plugin-homekit) |

If you know of a plugin not listed here let me know and I will add it to the list.
If you are a python developer and willing to implement a plugin for a service not listed here, let me know and I try to support you as good as possible

## Configuration
In your carconnectivity.json configuration add a section for the connectors you like to use like this:
```
{
    "carConnectivity": {
        "connectors": [
            {
                "type": "volkswagen",
                "config": {
                    "username": "test@test.de"
                    "password": "testpassword123"
                }
            },
            {
                "type": "skoda",
                "config": {
                    "username": "test@test.de"
                    "password": "testpassword123"
                }
            }
        ]
    }
}
```
The detailed configuration options of the connectors can be found in their README files.

## Getting started
- To get started have a look in the [examples folder](https://github.com/tillsteinbach/CarConnectivity/tree/main/examples)
