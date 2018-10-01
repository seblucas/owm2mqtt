# owm2mqtt

Get temperature, humidity values from  from https://openweathermap.org/ (OpenWeatherMap) and send it to your MQTT broker 

# Why ?

I did not find anything as simple as sending the data to a MQTT broker so I had to build it with python.

# Usage

## Prerequisite

You simply need Python3 (never tested with Python2.7) and the only dependencies are `requests` (to access the api) and `paho-mqtt` (for MQTT broker interaction) so this line should be enough  :

```bash
pip3 install paho-mqtt requests
```

## Getting your API token

First you'll have to get tour [API Key](https://openweathermap.org/appid). Then you can use the demo to find the city's ID you're interested in.

## Using the script

Easy, first try a dry-run command :

```bash
./owm2mqtt.py -c '<CITY_ID>' -a '<API_KEY>' -n -v
```

and then a real command to add to your crontab :

```bash
./owm2mqtt.py -c '<CITY_ID>' -a '<API_KEY>'
```

The secrets can also be set with environment variables, see the help for more detail.

## Help

```bash
/ # owm2mqtt.py --help
usage: owm2mqtt.py [-h] -a OWMAPIKEY -c CITY [-m HOST] [-n]
                   [-o PREVIOUSFILENAME] [-t TOPIC] [-T TOPIC] [-v]

Read current temperature and humidity from OpenWeatherMap and send them to a
MQTT broker.

optional arguments:
  -h, --help            show this help message and exit
  -a OWMAPIKEY, --owm-api-key OWMAPIKEY
                        OpenWeatherMap API Key. (default: None)
  -c CITY, --city CITY  OpenWeatherMap city ID. (default: None)
  -m HOST, --mqtt-host HOST
                        Specify the MQTT host to connect to. (default:
                        127.0.0.1)
  -n, --dry-run         No data will be sent to the MQTT broker. (default:
                        False)
  -o PREVIOUSFILENAME, --last-time PREVIOUSFILENAME
                        The file where the last timestamp coming from OWM API
                        will be saved (default: /tmp/owm_last)
  -t TOPIC, --topic TOPIC
                        The MQTT topic on which to publish the message (if it
                        was a success). (default: sensor/outdoor)
  -T TOPIC, --topic-error TOPIC
                        The MQTT topic on which to publish the message (if it
                        wasn't a success). (default: error/sensor/outdoor)
  -v, --verbose         Enable debug messages. (default: False)

```

## Other things to know

I personaly use cron to start this program so as I want to keep the latest timestamp received from the API, I store it by default in `/tmp/owm_last` (you can change it through a command line parameter).

## Docker

I added a sample Dockerfile, I personaly use it with a `docker-compose.yml` like this one :

```yml
version: '3'

services:
  waqi:
    build: https://github.com/seblucas/i2c2mqtt.git
    image: owm2mqtt-python3-cron:latest
    restart: always
    environment:
      OWM_API_KEY: YOUR_API_KEY
      OWM_CITY_ID: "YOUR_CITY_ID"
      CRON_STRINGS: "09 * * * * owm2mqtt.py -m localhost -v"
      CRON_LOG_LEVEL: 8
```

# Limits

None, I hope at least ;). I had to adjust the timestamp provided, it seems to fit with my locale (France) but it may need some additional work. 

# License

This program is licenced with GNU GENERAL PUBLIC LICENSE version 3 by Free Software Foundation, Inc.
