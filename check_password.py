#!/usr/bin/env python3

"""
Copyright 2025 Venko Moyankov

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


# Check if your password has been previously exposed in data breaches
#
# See https://haveibeenpwned.com/Passwords

import hashlib
from getpass import getpass
import urllib.request


password = getpass("Your password (will not be send anywhere): ")

pass_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
hash_prefix = pass_hash[:5]
hash_suffix = pass_hash[5:].encode("utf-8")


url = f"https://api.pwnedpasswords.com/range/{hash_prefix}"
print("Requesting ", url)

with urllib.request.urlopen(url) as f:
    for line in f:
        h, num = line.split(b":")
        num = int(num)
        if h == hash_suffix:
            print(f"Your password is found {num} times")
            exit(0)

print("Your password is not found")
