from lib import *

def start():
    clear_leds()
    rainbow()
    sleep_ms(2000)
    clear_leds()

    while True:
        read_buttons()
        for button in buttons:
            player = button.get_pressed()
            if player:
                button.set_led(player.color)
        leds.write()
