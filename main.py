# hiletgo esp32 pn532 rfid test script
import machine
import ssd1306
# Uses Adafruit PN532 NFC/RFID control library.
# Author: Tony DiCola
# pn_532_i2c wrapper updated by David Somerville to work with Micropython
import pn532_i2c
import time
from micropython import const
import network
import gc
# MicroWebCli is a micro HTTP Web client for MicroPython see https://github.com/jczic/MicroWebCli
from microWebCli import MicroWebCli

ALEXA_LAMP_URL = "http://192.168.1.115:1880/alexa"

NDEF_URIPREFIX_HTTP_WWWDOT = const(0x01)
NDEF_URIPREFIX_HTTPS_WWWDOT = const(0x02)
NDEF_URIPREFIX_HTTP = const(0x03)
NDEF_URIPREFIX_HTTPS = const(0x04)

TLV_START = const(0x00)
TLV_TYPE_NDEF = const(0x03)
NDEF_HEADER_WELL_KNOWN_TYPE = const(0xd1)
NDEF_PAYLOAD_TYPE_URI = const(0x55)


# Set up I2C buss and scan for devices
i2c = machine.I2C(1, scl=machine.Pin(22), sda=machine.Pin(21))
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

time.sleep_ms(1000)
# Setup network connection
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to guest network...')
    sta_if.active(True)
    sta_if.connect('guest24', 'backyard')
    while not sta_if.isconnected():
        time.sleep_ms(500)
        print("*", end="")
        pass
print('network config:', sta_if.ifconfig())
gc.collect()

# Start listening for a card
time.sleep_ms(1000)
print("Waiting for RFID/NFC card...")
gc.collect()
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
        gc.collect()
        # Process new RFID card
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
        # For NCF cards pull data to check for NDEF record
        # print("len(uid):", len(uid))
        if len(uid) == 7:
            # # Get first 176 bytes of data on the card
            try:
                cardData = pn532.mifare_classic_read_block(0)
                for blockNumber in range(3, 43, 4):
                    cardData += pn532.mifare_classic_read_block(blockNumber)
            except:
                print("Failed block read")
                pass
            print("Found card with UID:", [hex(i) for i in uid], uid)
            #  If card has a NDEF URL data
            #  First check card has a TLV block
            if (cardData[19] == TLV_START and cardData[20] == TLV_TYPE_NDEF):
                # Check TLV block has a NDEF record
                if (cardData[22] == NDEF_HEADER_WELL_KNOWN_TYPE and cardData[23] == 0x01):
                    # Check if data is URI
                    if (cardData[25] == NDEF_PAYLOAD_TYPE_URI):
                        # Get URI length
                        uriLength = cardData[24]
                        # Add the URL prefix
                        if cardData[26] == NDEF_URIPREFIX_HTTP_WWWDOT:
                            sURL = "http://www."
                        if cardData[26] == NDEF_URIPREFIX_HTTPS_WWWDOT:
                            sURL = "https://www."
                        if cardData[26] == NDEF_URIPREFIX_HTTP:
                            sURL = "http://"
                        if cardData[26] == NDEF_URIPREFIX_HTTPS:
                            sURL = "https://"
                        sURL += (cardData[27: uriLength -
                                          1 + 27]).decode('utf-8')
                        #  Call the URL
                        try:
                            print("Calling: ", sURL)
                            resp1 = MicroWebCli.GETRequest(
                                sURL, connTimeoutSec=3)
                        except:
                            print("http get failed")
        else:
            print()
            print("Found card with UID:", [hex(i) for i in uid])

    last_uid = uid
