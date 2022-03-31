# hiletgo esp32 pn532 rfid test script
import machine
import ssd1306
# Uses Adafruit PN532 NFC/RFID control library.
# Author: Tony DiCola
# pn_532_i2c wrapper updated by David Somerville to work with Micropython
import pn532_i2c
import time
from micropython import const


# Set up I2C buss and scan for devices
i2c = machine.I2C(1, scl=machine.Pin(15), sda=machine.Pin(4))
devices = i2c.scan()
if len(devices) == 0:
    print("No i2c device !")
else:
    print('i2c devices found:', len(devices))
    for device in devices:
        print("Decimal address: ", device, " | Hex address: ", hex(device))

# Defaults to i2c address 3C in SSD1306 library
pin = machine.Pin(16, machine.Pin.OUT)
pin.value(0)  # set GPIO16 low to reset OLED
pin.value(1)  # while OLED is running, must set GPIO16 in high
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)
oled.text('RFID/NFC tag reader', 0, 0)
oled.text('Starting....', 0, 10)
oled.show()

# Try running pn532 RFID code
#  Initalize the PN532 object, use the GPIO pin(5) to reset the PN532 on each run
pn532 = pn532_i2c.PN532_I2C(i2c, debug=False, reset=5)
ic, ver, rev, support = pn532.get_firmware_version()
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
# Set up configuration for MiFare type cards
pn532.SAM_configuration()

# Start listening for a card
print("Waiting for RFID/NFC card...")
last_uid = None
while True:
    # Check if a card is available to read
    uid = pn532.read_passive_target(timeout=0.5)
    print(".", end="")
    # Try again if no card is available
    if uid is None:
        last_uid = None
        oled.fill(0)
        oled.show()
        continue
    if last_uid == uid:
        pass
    else:
        print("Found card with UID:", [hex(i) for i in uid])
        oled.fill(0)
        # Format short string showing UID
        suid = ""
        for i in uid:
            if len(suid) > 0:
                suid += ":"
            s = hex(i)[2:4]
            suid += s
        # Display result on OED
        oled.text('UID Found', 0, 0)
        oled.text(suid, 0, 10)
        oled.show()
        print("len(suid):", len(suid))
        if len(suid) == 7:
            data0 = pn532.mifare_classic_read_block(0)
            print("Data0:", [hex(i) for i in data0])

    last_uid = uid
