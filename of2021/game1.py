#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is an example how NOT TO MAKE a secure application!
# It is used in a game at Openfest 2021 https://www.openfest.org/2021/en/


import hashlib
import re

SECRET_CODE = "XXXX"  # It is replaced in the real application
URL = "http://example.com"

message = ("Здарвейте! Въведете вашето име (на латиница) и e-mail адрес за да "
        "участвате в нашата лотария и да спечелите тениска. "
        "Ако оставите на случайността, шансовете не са много големи, но "
        "с малко съобразителност и знания може много да ги повишите. "
        "Изходния код на програмата която определя печелившите можете да "
        f"намерите тук {URL}. Успех!")

def main():
    print(message)

    name=''
    email=''

    try:
        while not re.match(r'[\w\- ]+$', name):
            name = input("Име (на латиница): ")
        while not re.match(r'[\w\-\.]+@[a-zA-z_.-]+$', email):
            email = input("e-mail адрес: ")
    except UnicodeDecodeError as e:
        print("Bad encoding:", e)
        return
    except EOFError:
        print("Goodbye!")
        return

    m = hashlib.md5()
    m.update(name.encode('utf-8'))
    m.update(email.encode('utf-8'))

    h = m.hexdigest()
    if h.startswith('00'):
        print("Честито! Вие печелите.")
        print("Покажете този код за да получите наградата: ", SECRET_CODE)
    else:
        print("Съжалявам, не печелите. Може да опитате пак с друго име "
                "или e-mail адрес.")



if __name__ == '__main__':
    main()
