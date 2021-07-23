# abstraction layer for ble
# examples:
# + https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_simple_peripheral.py
# + https://github.com/2black0/MicroPython-ESP32-BLE/blob/main/main.py

import ubluetooth
import time
from micropython import const
from .ble_advertising import advertising_payload

# constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

# caution - in examples this is const(3). At ESP32 it was 4
# you can debug this in irq which value is fitting
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# unique service identifier - https://www.uuidgenerator.net/version4
# define service abilities
# uuid or characteristic https://www.bluetooth.com/specifications/gatt/characteristics/
# enable push(notify) and pull(read)
# https: // github.com/2black0/MicroPython-ESP32-BLE/blob/main/main.py
# https://github.com/poesel/BLE-uPy-Pycom/blob/master/uPy/main.py
_WS_UUID = ubluetooth.UUID("f715a766-9477-11eb-a8b3-0242ac130003")
# org.bluetooth.characteristic.weight_measurement
_WS_CHAR = (ubluetooth.UUID("0f07a13a-9478-11eb-a8b3-0242ac130003"),
            ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY,)
# serial send service without: https://stackoverflow.com/a/10252283/10101463
_WS_CMD = (ubluetooth.UUID("1c52cdcd-09b6-4d34-9689-1faba100f46f"),
           ubluetooth.FLAG_WRITE)

_WS_SERVICE = (_WS_UUID, (_WS_CHAR, _WS_CMD), )

# services you can get data from
_SERVICES = (_WS_SERVICE,)
# advertised services
_ADV_SERVICES = [_WS_UUID]
# set appearance - sets the icon
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE = const(0)  # const(3200)


class BLEx:
    # 31bit is max limit for payload so take short name
    def __init__(self, ble, name="ScX"):
        self._ble = ble
        self._name = name
        self.initBLE()

    def initBLE(self):
        # set ble active
        self._ble.config(gap_name=self._name)
        self._ble.active(True)

        # register eventhandler
        self._ble.irq(self._irq)

        # register service
        ((self._handle_tx, self._handle_rx),
         ) = self._ble.gatts_register_services(_SERVICES)

        # gats buffer https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_uart_peripheral.py#L40
        self._ble.gatts_set_buffer(self._handle_rx, 100, True)
        self._rx_buffer = bytearray()

        # store connections in set
        self._connections = set()

        # trigger function if reciving something from client
        self._write_callback = None

        # calculate advertising payload, getting OSError: [Errno 5] EIO with to big payload
        # appearance=_ADV_APPEARANCE_GENERIC_COMPUTER,
        self._payload = advertising_payload(
            name=self._name, services=_ADV_SERVICES, appearance=_ADV_APPEARANCE)

        # start advertising service
        self._advertise()

        return

    # listen to various events, depending on the role of the device
    # full list: https://docs.micropython.org/en/latest/library/ubluetooth.html#event-handling

    def _irq(self, event, data):
        # tracking client - connect
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("irq -> client connected:", conn_handle)
            self._connections.add(conn_handle)
        # tracking client - disconnect
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("irq -> client disconected:", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()

        # tracking other events
        # recive data from client
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data

            # simple version
            # # extract recieved values from handle
            # value = self._ble.gatts_read(value_handle)
            # print("recieve data from", conn_handle, "|", value)
            # if value_handle == self._handle_rx and self._write_callback:
            #     self._write_callback(value)

            # buffered version
            # pass values to callback
            if conn_handle in self._connections and value_handle == self._handle_rx:
                self._rx_buffer += self._ble.gatts_read(self._handle_rx)
                if self._write_callback:
                    self._write_callback()

    # register function to recive event
    def onRecive(self, callback):
        self._write_callback = callback

    def any(self):
        return len(self._rx_buffer)

    # read buffered - https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_uart_peripheral.py
    def read(self, sz=None):
        if not sz:
            sz = len(self._rx_buffer)
        result = self._rx_buffer[0:sz]
        self._rx_buffer = self._rx_buffer[sz:]
        return result

    # start advertising
    def _advertise(self, interval_us=500000):
        # avoid OSError: [Errno 5] EIO
        time.sleep(1)
        print("init: starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    # send data to all connected clients
    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)
