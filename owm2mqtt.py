#!/usr/bin/env python3
#
#  owm2mqtt.py
#
#  Copyright 2016 Sébastien Lucas <sebastien@slucas.fr>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


import os, re, time, json, argparse
import requests                     # pip install requests
import paho.mqtt.publish as publish # pip install paho-mqtt

owLastDt = None
verbose = False
OPEN_WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?id={0}&units=metric&lang=fr&appid={1}'

def debug(msg):
  if verbose:
    print (msg + "\n")

def environ_or_required(key):
  if os.environ.get(key):
    return {'default': os.environ.get(key)}
  else:
    return {'required': True}

def getOpenWeather(city, apiKey):
  global owLastDt
  tstamp = int(time.time())
  owmUrl = OPEN_WEATHER_URL.format(city, apiKey)
  debug ("Trying to get data from {0}".format(owmUrl))
  try:
    r = requests.get(owmUrl)
    data = r.json()
    if not 'dt' in data or not 'main' in data or not 'temp' in data['main']:
      return (False, {"time": tstamp, "message": "OpenWeatherMap data not well formed", "data": data})
    newObject = {"time": data['dt'], "temp": data['main']['temp'], "hum": data['main']['humidity']}
    return (True, newObject)
  except requests.exceptions.RequestException as e:
    return (False, {"time": tstamp, "message": "OpenWeatherMap not available : " + str(e)})


parser = argparse.ArgumentParser(description='Read current temperature and humidity from OpenWeatherMap and send them to a MQTT broker.',
  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-a', '--owm-api-key', dest='owmApiKey', action="store",
                   help='OpenWeatherMap API Key.',
                   **environ_or_required('OWM_API_KEY'))
parser.add_argument('-c', '--city', dest='city', action="store",
                   help='OpenWeatherMap city ID.',
                   **environ_or_required('OWM_CITY_ID'))
parser.add_argument('-m', '--mqtt-host', dest='host', action="store", default="127.0.0.1",
                   help='Specify the MQTT host to connect to.')
parser.add_argument('-n', '--dry-run', dest='dryRun', action="store_true", default=False,
                   help='No data will be sent to the MQTT broker.')
parser.add_argument('-o', '--last-time', dest='previousFilename', action="store", default="/tmp/owm_last",
                   help='The file where the last timestamp coming from OWM API will be saved')
parser.add_argument('-t', '--topic', dest='topic', action="store", default="sensor/outdoor",
                   help='The MQTT topic on which to publish the message (if it was a success).')
parser.add_argument('-T', '--topic-error', dest='topicError', action="store", default="error/sensor/outdoor", metavar="TOPIC",
                   help='The MQTT topic on which to publish the message (if it wasn\'t a success).')
parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,
                   help='Enable debug messages.')


args = parser.parse_args()
verbose = args.verbose;

status, data = getOpenWeather(args.city, args.owmApiKey)
jsonString = json.dumps(data)
if status:
  debug("Success with message <{0}>".format(jsonString))
  if os.path.isfile(args.previousFilename):
    oldTimestamp = open(args.previousFilename).read(10);
    if int(oldTimestamp) >= data["time"]:
      print ("No new data found")
      exit(0)

  # save the last timestamp in a file
  with open(args.previousFilename, 'w') as f:
    f.write(str(data["time"]))
  if not args.dryRun:
    publish.single(args.topic, jsonString, hostname=args.host)
else:
  debug("Failure with message <{0}>".format(jsonString))
  if not args.dryRun:
    publish.single(args.topicError, jsonString, hostname=args.host)

