from lib import *
import random

def start(repeat=3):

    for i in range(repeat):
        clear_leds()
        for b in buttons:
            b.set_led(WHITE)
        leds.write()
        #sleep_ms(3000)
        #clear_leds()
        sleep_ms(random.randrange(1000,7000))
        all_colors = COLORS8[:]
        for button in buttons:
            idx = random.randrange(len(all_colors))
            color = all_colors.pop(idx)
            button.set_led(color)
        leds.write()
        winner = None
        while not winner:
            read_buttons()
            for b in buttons:
                p = b.get_pressed()
                if p and p.color == b.get_led():
                    winner = p
        clear_leds()
        sleep_ms(1000)
        for i in range(5):
            for button in buttons:
                button.set_led(winner.color)
            leds.write()
            sleep_ms(250)
            clear_leds()
            sleep_ms(250)


