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
PAD_PINS = [ 26, 35, 39, 23, 22, 36, 34, 25 ]
NP_LED = 27
LVL = 21
NUM_PADS = len(PAD_PINS)
NUM_PLAYERS = len(PLAYER_PINS)
COLORS8 = [
        (255, 0, 0),   # 0 Red
        (192, 32, 0),  # 1 Orange
        (128, 80, 0),  # 2 Yellow
        (0, 255, 0),   # 3 Green
        (16, 64, 64), # 4 Cyan
        (0, 0, 255),   # 5 Blue
        (64, 0, 192),   # 6 Violet
        (128, 0, 32),   # 7 Magenta
        ]
COLORS4 = [ COLORS8[i] for i in (0, 2, 3, 5) ]

class Player:
    def __init__(self, pin, color=None, result=0):
        self.pin = Pin(pin, Pin.OUT, value=1)
        self.result = result
        self.color = color

class Pad:
    def __init__(self, pin, led_idx):
        self.pin = Pin(pin, Pin.IN)
        self.pressed = {}
        self.led_idx = led_idx

    def init_plyers(self, players):
        for p in players:
            self.pressed[p] = False

    def get_pressed(self, player):
        # Call this after read_pads()
        return self.pressed[player]



players = [ Player(x) for x in PLAYER_PINS ]
pads = [ Pad(x, i) for x,i in zip(PAD_PINS, range(NUM_PADS)) ]
leds = NeoPixel(Pin(NP_LED, Pin.OUT), NUM_PADS)
level = Pin(LVL, Pin.OUT, value=1)

def clear_leds():
    for i in range(NUM_PADS):
        leds[i] = (0, 0, 0)
    leds.write()

def rainbow():
    for i in range(NUM_PADS):
        leds[i] = COLORS8[i]
    leds.write()

def read_pads():
    for l in players:
        l.pin.value(1)
    for pad in pads:
        if pad.pin.value() == 0:
            raise ValueError("%s is down!" % pad)
    for l in players:
        l.pin.value(0)
        for pad in pads:
            pad.pressed[l] = (pad.pin.value() == 0)
        l.pin.value(1)

def read_pad1(pad):
    pressed = { x: False for x in players }
    for l in players:
        l.pin.value(1)
    if pad.pin.value() == 0:
        raise ValueError("%s is down!" % pad)
    for l in players:
        l.pin.value(0)
        pressed[l] = (pad.pin.value() == 0)
        l.pin.value(1)
    return pressed

def show_ok(res):
    clear_leds()
    sleep_ms(100)
    for i in range(NUM_PLAYERS):
        if res[i]:
            for j in range(NUM_PADS):
                leds[j] = COLORS[i]
            leds.write()
        sleep_ms(2000)
    clear_leds()

def show_error(res):
    for k in range(5):
        clear_leds()
        sleep_ms(500)
        if res is None:
            for j in range(NUM_PADS):
                leds[j] = (255, 255, 255)
            leds.write()
            sleep_ms(500)
        else:
            for i in range(NUM_PLAYERS):
                if res[i]:
                    for j in range(NUM_PADS):
                        leds[j] = COLORS[i]
                    leds.write()
                    sleep_ms(500)

    clear_leds()


def get_players(pad, res):
    for p in players:
        p.off()
    if pad.value():
        raise ValueError
    for i in range(len(players)):
        players[i].on()
        res[i] = pad.value()
        players[i].off()
        if pad.value():
            raise ValueError
    return res


clear_leds()
