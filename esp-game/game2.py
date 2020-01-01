from lib import *
import random

def start(repeat=3):

    for i in range(repeat):
        clear_leds()
        button = buttons[0]
        rand_color = random.choice(COLORS8)
        button.set_led(rand_color)
        leds.write()
        sleep_ms(3000)
        clear_leds()
        sleep_ms(random.randrange(1000,7000))
        all_colors = COLORS8[:]
        for button in buttons:
            idx = random.randrange(len(all_colors))
            color = all_colors.pop(idx)
            button.set_led(color)
            if color == rand_color:
                correct_button = button
        leds.write()
        winner = None
        while not winner:
            read_buttons()
            winner = correct_button.get_pressed()
        clear_leds()
        sleep_ms(1000)
        for i in range(5):
            for button in buttons:
                button.set_led(winner.color)
            leds.write()
            sleep_ms(250)
            clear_leds()
            sleep_ms(250)


