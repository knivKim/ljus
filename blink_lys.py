"""Provide a CLI for Tradfri."""
import logging
from pprint import pprint

from pytradfri.const import *  # noqa
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.util import load_json, save_json
from pytradfri.error import PytradfriError
from pytradfri.gateway import Gateway
from pytradfri.command import Command

import time
import argparse
import uuid
import random

from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, XYZColor

CONFIG_FILE = 'tradfri_standalone_psk.conf'

#logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('--host',required=False,default="192.168.0.108", type=str,
                    help='IP Address of your Tradfri gateway')
parser.add_argument('-K', '--key', dest='key', required=False,
                    help='Security code found on your Tradfri gateway')
args = parser.parse_args()

if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print("Please provide the 'Security Code' on the back of your "
          "Tradfri gateway:", end=" ")
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("'Security Code' has to be exactly" +
                             "16 characters long.")
    else:
        args.key = key

conf = load_json(CONFIG_FILE)

try:
    identity = conf[args.host].get('identity')
    psk = conf[args.host].get('key')
    api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
except KeyError:
    identity = uuid.uuid4().hex
    api_factory = APIFactory(host=args.host, psk_id=identity)

    try:
        psk = api_factory.generate_psk(args.key)
        print('Generated PSK: ', psk)

        conf[args.host] = {'identity': identity,
                           'key': psk}
        save_json(CONFIG_FILE, conf)
    except AttributeError:
        raise PytradfriError("Please provide the 'Security Code' on the "
                             "back of your Tradfri gateway using the "
                             "-K flag.")

api = api_factory.request

gateway = Gateway()
devices_commands = api(gateway.get_devices())
devices = api(devices_commands)
lights = [dev for dev in devices if dev.has_light_control]
if lights:
    light = lights[0]
else:
    print("No lights found!")
    light = None
groups = api(gateway.get_groups())
if groups:
    group = groups[0]
else:
    print("No groups found!")
    group = None
moods = api(gateway.get_moods())
if moods:
    mood = moods[0]
else:
    print("No moods found!")
    mood = None
tasks = api(gateway.get_smart_tasks())
homekit_id = api(gateway.get_gateway_info()).homekit_id

def dump_all():
    endpoints = api(gateway.get_endpoints())

    for endpoint in endpoints:
        parts = endpoint[1:].split('/')

        if not all(part.isdigit() for part in parts):
            continue

        pprint(api(Command('get', parts)))
        print()
        print()

def dump_devices():
    pprint([d.raw for d in devices])
        
gron = (26870, 33423)
rod = (42926, 21299)
blaa = (11469, 3277)
rosa = (32768, 15729)
limeGron = (29491, 30802)
varmKvit = (32977, 27105)
blaaKvit = (25022, 24884)

listeAvFarger = [gron, rod, blaa, rosa, limeGron, varmKvit,blaaKvit]

lightOrder = [0,1,2] #Skriv in ljusa i rekkefølge frå badet til kjøkenet, denne vert nytta til posisjonsavhengige iterasjonsalgoritmer

def blink_on_off(sleepTime=0.2,wakeTime=0.5,transition_time = 0.0001,rand_colour = False):
    #blinker alle lysene på også av samtidig. 
    if not rand_colour: 
        colour = blaaKvit
        for i in range(0,len(lights)):
            api(lights[i].light_control.set_xy_color(colour[0],colour[1]))
    
    for i in range(0,len(lights)):
        if rand_colour: 
            colour = (random.randint(9,60000),random.randint(9,60000))
            api(lights[i].light_control.set_xy_color(colour[0],colour[1]))
        api(lights[i].light_control.set_dimmer(100,transition_time=transition_time))
    time.sleep(wakeTime)
    
    for i in range(0,len(lights)):
        api(lights[i].light_control.set_dimmer(0,transition_time=transition_time))
    time.sleep(sleepTime)
    '''
    api(groups[0].light_control.set_dimmer(0))
    time.sleep(sleepTime)
    api(groups[0].light_control.set_dimmer(100))
    time.sleep(sleepTime)
    '''
def chaotic_blink():
    #tilfeldig farge og tilfeldig brightness
    for i in range(0,len(lights)):
        api(lights[i].light_control.set_xy_color(random.randint(9,60000),random.randint(9,60000)))
        brightness = random.randint(0,100)
        time.sleep(0.15)
        if brightness < 21:
            brightness = 0
        api(lights[i].light_control.set_dimmer(brightness))

def predetermined():
    #FOrhandsbestemte farger og brightness for enkelte lys
    colour = listeAvFarger[random.randint(0,len(listeAvFarger)-1)]
    api(lights[0].light_control.set_xy_color(colour[0],colour[1]))
    api(lights[0].light_control.set_dimmer(random.randint(0,100)))
    api(lights[1].light_control.set_xy_color(colour[0],colour[1]))
    api(lights[1].light_control.set_dimmer(random.randint(0,100)))
    colour = listeAvFarger[random.randint(0,len(listeAvFarger)-1)]
    api(lights[2].light_control.set_xy_color(colour[0],colour[1]))
    api(lights[2].light_control.set_dimmer(random.randint(0,100)))
    time.sleep(1)

def synch_brightness(sleepTime=0.3):
    #Skifter farger kvart tidsintervall til individuelle farger
    #ljusa deler ljusstyrke
    brightness = random.randint(0,100)
    if brightness < 21:
        brightness = 0
    for i in range(0,len(lights)):
        api(lights[i].light_control.set_xy_color(random.randint(9,60000),random.randint(9,60000)))
        api(lights[i].light_control.set_dimmer(brightness))
    time.sleep(sleepTime)

def synch_all(sleepTime=0.5):
    #Skifter farger kvart tidsintervall til individuelle farger
    #ljusa deler ljusstyrke
    brightness = random.randint(0,100)
    colour = (random.randint(9,60000),random.randint(9,60000))
    if brightness < 21:
        brightness = 0
    for i in range(0,len(lights)):
        api(lights[i].light_control.set_xy_color(colour[0],colour[1]))
        api(lights[i].light_control.set_dimmer(brightness))
    time.sleep(sleepTime)


def light_train(speed, minBrightness, maxBrightness, orderOfLights):
    #speed er eit mål på hastigheita til lysskiftinga
    #maxBrightness er den maksimale ljusstyrka til ljusa
    #minBrightness er den minimale ljusstyrka til ljusa
    for setColour in range(0,len(lights)):
        api(lights[setColour].light_control.set_xy_color(varmKvit[0],varmKvit[1]))
    for darkest in orderOfLights:
        for offset in orderOfLights:
            currentLight = (darkest + offset)%len(lights)
            currentBrightness = int(minBrightness + (maxBrightness-minBrightness)*(offset/(len(lights)-1)))
            #print('Current light is: ' + str(currentLight))
            #print('CurrentBrightness is: ' + str(currentBrightness))
            api(lights[currentLight].light_control.set_dimmer(currentBrightness))
            time.sleep(speed)

while 1:
    blink_on_off(rand_colour = True)
    #synch_brightness(0.3)
    #synch_all()
    #light_train(0.2,0,100, lightOrder)
    #chaotic_blink()

