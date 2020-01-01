from lib import *
import game1, game2, game3

while True:
    choice = menu(3)
    if choice == 0:
        game1.start()
    if choice == 1:
        game2.start()
    if choice == 2:
        game3.start()
