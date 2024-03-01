#!/usr/bin/env python
# -*- coding: utf-8 -*-

from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
import random
from umqtt.simple import MQTTClient
import machine

from tz import localtime
from settings import Config

LED_PIN        = 13
LED_COUNT      = 25      # Number of LED pixels.

effects = {
        b"colors": True,
        b"theater": False,
        b"rb": True,
        b"rbc": True,
        b"chase": False,
}

mqttc = None
break_ = False

def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)

    if wlan.isconnected():
        print('network config:', wlan.ifconfig())
        return

    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(Config.ssid, Config.wifi_pass)
        for _ in range(10):
            if wlan.isconnected():
                print('network config:', wlan.ifconfig())
                return
            sleep_ms(1000)
            print("Waiting to connect ...")
        print("No Wifi connection. Continue ...")
        #machine.reset()


def connect_broker():

    c = MQTTClient(Config.CLIENT_ID, Config.SERVER, user=Config.USER, password=Config.PASSWORD)
    c.DEBUG = True
    c.keepalive = 30
    # Subscribed messages will be delivered to this callback
    c.set_callback(mqtt_cb)
    c.set_last_will("status/connected", "DISCONNECTED", retain=True, qos=1)
    c.connect()
    c.subscribe(Config.TOPIC, qos=1)
    print("Connected to %s, subscribed to %s topic" % (Config.SERVER, Config.TOPIC))
    lt = localtime()
    c.publish("status/connected",
            "Connected at %4d-%02d-%02d %02d:%02d:%02d" % lt[:6],
            retain=True
    )
    return c


def mqtt_cb(topic, msg):
    global effects, break_

    print("received", topic, msg)
    t = topic.split(b"/")
    if t[0] != b"xmass" or len(t) != 2:
        return
    if t[1] in effects:
        effects[t[1]] = (msg == b"1")
    if t[1] == b"break":
        break_ =  True



# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    global mqttc
    for i in range(strip.n):
        strip[i] = color
        strip.write()
        sleep_ms(wait_ms)
        if mqttc: mqttc.check_msg()
        if break_: return None

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    global mqttc, break_
    for j in range(iterations):
        for q in range(3):
            for i in range(q, strip.n, 3):
                strip[i] = color
            strip.write()
            sleep_ms(wait_ms)
            if mqttc: mqttc.check_msg()
            if break_: return None
            for i in range(q, strip.n, 3):
                strip[i] = (0, 0, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    global mqttc, break_
    for j in range(256*iterations):
        for i in range(strip.n):
            strip[i] = wheel((i+j) & 255)
        strip.write()
        sleep_ms(wait_ms)
        if mqttc: mqttc.check_msg()
        if break_: return None


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    global mqttc, break_
    for j in range(256*iterations):
        for i in range(strip.n):
            strip[i] = wheel(int(i * 256 / strip.n + j) & 255)
        strip.write()
        sleep_ms(wait_ms)
        if mqttc: mqttc.check_msg()
        if break_: return None

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    global mqttc, break_
    for j in range(0, 3*80, 80):
        for q in range(3):
            for i in range(q, strip.n, 3):
                strip[i] = wheel((i*5+j) % 255)
            strip.write()
            sleep_ms(wait_ms)
            if mqttc: mqttc.check_msg()
            if break_: return None
            for i in range(q, strip.n, 3):
                strip[i] = (0,0,0)

colors = [
    (255, 40, 192), # pink
    (255, 32, 0),   # orange
    (80, 0 , 255),  # violet
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 128, 0),  # yellow
    (0, 255, 128),  # cyan
    (255, 0, 64),   # magenta
    (127, 127, 127), # white
]

strip = NeoPixel(Pin(LED_PIN, Pin.OUT), LED_COUNT)


# Main program logic follows:
def main():
    global colors, strip, effects, mqttc, break_

    try:
        do_connect()
        mqttc = connect_broker()
    except:
        print("Can't connect. Continue offline")

    if mqttc: mqttc.publish("xmass/now", "Started", retain=True)

    while True:
        try:
            break_ = False

            sleep_ms(100)
            if mqttc: mqttc.check_msg()

            if effects[b'colors']:
                print('Color wipe animations.')
                if mqttc: mqttc.publish("xmass/now", "Colors", retain=True)
                for n in range(3):
                    for c in colors:
                        colorWipe(strip, c)
            else:
                print('SKIP: Color wipe animations.')

            if effects[b'theater']:
                print ('Theater chase animations.')
                if mqttc: mqttc.publish("xmass/now", "Theater", retain=True)
                theaterChase(strip, random.choice(colors))
            else:
                print ('SKIP: Theater chase animations.')

            if effects[b'rb']:
                print ('Rainbow animations.')
                if mqttc: mqttc.publish("xmass/now", "Rainbow", retain=True)
                rainbow(strip, 20, 5)
            else:
                print ('SKIP: Rainbow animations.')

            if effects[b'rbc']:
                print ('RainbowCycle.')
                if mqttc: mqttc.publish("xmass/now", "RainbowCycle", retain=True)
                rainbowCycle(strip, 5, 20)
            else:
                print ('SKIP: RainbowCycle.')

            if effects[b'chase']:
                print ('RainbowChase.')
                if mqttc: mqttc.publish("xmass/now", "Chase", retain=True)
                theaterChaseRainbow(strip, wait_ms=200)
            else:
                print ('SKIP: RainbowChase.')

        except OSError as e:
            print(e)
            mqttc = connect_broker()



if __name__ == '__main__':
    main()

