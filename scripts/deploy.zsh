# copy folder ble
rshell -p /dev/cu.usbserial-0001 mkdir /pyboard/scale
rshell -p /dev/cu.usbserial-0001 cp -r ../micropython/scale/ /pyboard/

# copy folder ble
rshell -p /dev/cu.usbserial-0001 mkdir /pyboard/ble
rshell -p /dev/cu.usbserial-0001 cp -r ../micropython/ble/ /pyboard/

# copy main.py
rshell -p /dev/cu.usbserial-0001 cp -r ../micropython/main.py /pyboard/
