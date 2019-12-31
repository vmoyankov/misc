from lib import *

def g():
    clear_leds()
    rainbow()
    rainbow()
    sleep_ms(1000)
    clear_leds()

    while True:
        read_pads()
        for pad in pads:
            np = 0
            for li, l in enumerate(players):
                if pad.get_pressed(l):
                    np += 1
                    leds[pad.led_idx]=COLORS4[li]
                    # print("Pad {} Player {}".format(pad.led_idx, li))
            if np > 1:
                leds[pad.led_idx]=(0,0,0)
                # print("Pad {} COUNT {}".format(pad.led_idx, np))
        leds.write()
