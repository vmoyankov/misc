#!/usr/bin/env python
# -*- coding: utf-8 -*-

from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
import random

LED_PIN        = 27
LED_COUNT      = 25      # Number of LED pixels.


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(len(strip)):
        strip[i] = color
        strip.write()
        sleep_ms(wait_ms)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, len(strip), 3):
                strip[i + q] = color
            strip.write()
            sleep_ms(wait_ms)
            for i in range(0, len(strip), 3):
                strip[i + q] = (0, 0, 0)

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
    for j in range(256*iterations):
        for i in range(len(strip)):
            strip[i] = wheel((i+j) & 255)
        strip.write()
        sleep_ms(wait_ms)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(len(strip)):
            strip[i] = wheel(int(i * 256 / len(strip) + j) & 255)
        strip.write()
        sleep_ms(wait_ms)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, len(strip), 3):
                strip[i+j] = wheel((i+j) % 255)
            strip.write()
            sleep_ms(wait_ms)
            for i in range(0, len(strip), 3):
                strip[i+q] = (0,0,0)

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
    global colors, strip

    try:

        while True:
            print('Color wipe animations.')
            for n in range(3):
                for c in colors:
                    colorWipe(strip, c)
            print ('Theater chase animations.')
            for n in range(0):
                theaterChase(strip, random.choice(colors))
            print ('Rainbow animations.')
            rainbow(strip, 20, 5)
            print ('RainbowCycle.')
            rainbowCycle(strip, 5, 20)
            print ('RainbowChase.')
            theaterChaseRainbow(strip)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()

