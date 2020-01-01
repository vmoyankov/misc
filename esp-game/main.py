from lib import *
import game1, game2

while True:
    choice = menu(2)
    if choice == 0:
        game1.start()
    if choice == 1:
        game2.start()
