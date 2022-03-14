# hiletgo ssd test
import machine
import ssd1306
import pn532_i2c
import time
from micropython import const
_I2C_ADDRESS = const(0x24)

pin = machine.Pin(16, machine.Pin.OUT)
pin.value(0)  # set GPIO16 low to reset OLED
pin.value(1)  # while OLED is running, must set GPIO16 in high

i2c = machine.I2C(1, scl=machine.Pin(15), sda=machine.Pin(4))
devices = i2c.scan()
if len(devices) == 0:
    print("No i2c device !")
else:
    print('i2c devices found:', len(devices))
    for device in devices:
        print("Decimal address: ", device, " | Hex address: ", hex(device))

# defaults to i2c address 3C in library
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text('MicroPython on', 0, 0)
oled.text('an ESP32 with an', 0, 10)
oled.text('attached SSD1306', 0, 20)
oled.text('OLED', 0, 30)
oled.show()

# Try running pn532 code
# pn532 = pn532_i2c.PN532_I2C(i2c, debug=True)
# ic, ver, rev, support = pn532.firmware_version
# print("ic:", ic, " ver:", ver, " rev:", rev, " support:", support)
while True:
    time.sleep_ms(100)
    # print("x", "")
    status = bytearray(1)
    i2c.readfrom_into(_I2C_ADDRESS, status)
    # print(i2c.readfrom(_I2C_ADDRESS, 1), ".")
