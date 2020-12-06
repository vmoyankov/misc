To build and install on ESP32 you need:

::

  apt install cu
  pip3 install esptool
  pip3 install adafruit-ampy
  
Optional ::

  pip3 install mpy-cross

Check ESP32 has micropython installed::

  cu -l /dev/ttyUSB0 -s 115200 -f

Press <ctrl-C> and check for ``>>>`` prompt.

Flash ESP32 with micropython if needed::

  wget https://micropython.org/resources/firmware/esp32-idf3-20200902-v1.13.bin
  esptool.py --port /dev/ttyUSB0 erase_flash
  esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-idf3-20200902-v1.13.bin

See details at: https://docs.micropython.org/en/latest/esp32/tutorial/intro.html

Using the filesystem
---------------------

::

  export AMPY_PORT=/dev/ttyUSB0
  ampy ls

Upload files::

  ampy put main.py
  ampy put xmass.py

Pre-Compile python files (Optional)
---------------------------------

This is an optional step to pre-compile python files. This will free some RAM.

::

  python -m mpy_cross xmass.py
  ampy rm xmass.py
  ampy put xmass.mpy
