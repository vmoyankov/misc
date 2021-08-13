#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is an example how NOT TO MAKE a secure application!
# It is used in a game at Openfest 2021 https://www.openfest.org/2021/en/


import hashlib
import re
import subprocess

SECRET_CODE = "XXXX"  # It is replaced in the real application
URL = "http://example.com"


message = f"""
            Здравейте! Благодарим ви, че се включвате в играта организирана от
            StorPool Storage за OpenFest 2021!

            За да участвате, въведете реален e-mail адрес, на който ще получите
            потвърждение за успешното решаване на задачата.

            Не оставяйте нищо на случайността! С малко съобразителност и
            хакерски умения, можете да повишите вашите шансове и да спечелите
            свежа StorPool тениска.  Наградата може да получите на нашия щанд
            на OpenFest 2021 или с куриер до ваш адрес.

            Изходният код на програмата, с която можете да хакнете играта на
            StorPool, ще намерите тук {URL}

            Успех! Нека силата бъде с вас!
"""

def main():
    print(message)

    name = None
    email = None

    try:
        while True:
            name = input("Име: ")
            if re.match(r'[\w\- ]+$', name):
                break
            print("Невалиден формат.")

        while True:
            email = input("e-mail адрес: ")
            if re.match(r'[\w\-\.]+@[a-zA-z_.-]+$', email):
                break
            print("Невалиден формат.")

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
        print("Честито! Вие печелите!")
        print(f"Изпратихме Ви информация как да получите наградата си на посочения от Вас адрес {email}")
        send_confirmation(email, name)
    else:
        print("Съжалявам, не печелите. Може да опитате пак с друго име "
                "или e-mail адрес.")


def send_confirmation(email, name):
    try:
        subprocess.run(["./send_message", email, name])
    except subprocess.CalledProcessError as e:
        print("Error sending email", e)

if __name__ == '__main__':
    main()
