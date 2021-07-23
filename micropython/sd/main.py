print('sd card sample loaded')

import machine, os, uos

# for esp32 - https://docs.micropython.org/en/latest/library/machine.SDCard.html
print('v1')
# sd = machine.SDCard(slot=2, mosi=23, miso=19, sck=18, cs=5, freq=10000000)
sd = machine.SDCard()
uos.mount(sd, "/sd")
ld = os.listdir('/sd')

print('files', [x for x in ld])


