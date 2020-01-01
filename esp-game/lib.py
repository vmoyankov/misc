#!/usr/bin/env python
# -*- coding: utf-8 -*-

from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms

#PLAYER_PINS = [ 36, 39, 34, 35 ]
#PAD_PINS = [ 11, 10, 9, 13 ,12, 14, 27, 26 ]
#NP_LED = 25
PLAYER_PINS = [ 19, 18, 5, 17 ]
#PAD_PINS = [ 26, 25, 35, 34, 39, 36, 23, 22 ]
BUTTON_PINS = [ 26, 35, 39, 23, 22, 36, 34, 25 ]
NP_LED = 27
LVL = 21
NUM_BUTTONS = len(BUTTON_PINS)
NUM_PLAYERS = len(PLAYER_PINS)
RED      = (255,   0,   0)
ORANGE   = (192,  32,   0)
YELLOW   = (128,  80,   0)
GREEN    = (  0, 255,   0)
CYAN     = ( 16,  64,  64)
BLUE     = (  0,   0, 255)
PINK     = ( 64,   0, 192)
VIOLET   = (128,   0,  32)
WHITE    = (128, 128, 128)
COLORS8 = [ RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PINK, VIOLET ]
COLORS4 = [ RED, GREEN, YELLOW, PINK ]
WHITE

class Player:
    def __init__(self, pin, color=None, result=0):
        self.pin = Pin(pin, Pin.OUT, value=1)
        self.result = result
        self.color = color

class Button:
    def __init__(self, pin, led_id):
        self.pin = Pin(pin, Pin.IN)
        self.led_id = led_id
        self.pressed = None

    def get_pressed(self):
        # Call this after read_pads()
        return self.pressed

    def get_led(self):
        global leds
        return leds[self.led_id]

    def set_led(self, color):
        global leds
        leds[self.led_id] = color


players = [ Player(x, COLORS4[i]) for i,x in enumerate(PLAYER_PINS) ]
buttons = [ Button(x, i) for i,x in enumerate(BUTTON_PINS) ]
leds = NeoPixel(Pin(NP_LED, Pin.OUT), NUM_BUTTONS)
level = Pin(LVL, Pin.OUT, value=1)

def clear_leds():
    global leds
    for b in buttons:
        b.set_led((0,0,0))
    leds.write()

def rainbow():
    global leds
    for i,b in enumerate(buttons):
        b.set_led(COLORS8[i])
    leds.write()

def read_buttons():
    for l in players:
        l.pin.value(1)
    for b in buttons:
        if b.pin.value() == 0:
            print("Button {} is down!".format(b))
        b.pressed = None
    for l in players:
        l.pin.value(0)
        for b in buttons:
            if b.pin.value() == 0:
                b.pressed = l
        l.pin.value(1)

def select(choices=NUM_BUTTONS):
    while True:
        read_buttons()
        for i in range(choices):
            b = buttons[i]
            if b.pressed:
                return i

def menu(choices):
    clear_leds()
    for b in buttons:
        b.set_led(WHITE)
        leds.write()
        sleep_ms(125)
    clear_leds()
    for i in range(choices):
        b = buttons[i]
        b.set_led(COLORS8[i])
    leds.write()
    res = select(choices)
    for i in range(3):
        buttons[res].set_led(COLORS8[res])
        leds.write()
        sleep_ms(250)
        clear_leds()
        sleep_ms(250)
    return res

clear_leds()
