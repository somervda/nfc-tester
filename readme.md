## Micropython pn532 rfid/nfc reader/writer code for I2C interface

This uses the adafruit pn532 libraries at https://github.com/adafruit/Adafruit_CircuitPython_PN532
but with updated pn532_i2c.pn to allow it to work with standard micropython
rather than circuit python.

main.py includes sample code for 
1. Initializing and scanning the i2c bus
2. ssd1306 code to use a OLED display to show rfid tag information
3. pn532 code to read uid infomation on rfid and nfc tags

### Reference Documents
- pn532 datasheet https://www.nxp.com/docs/en/nxp/data-sheets/PN532_C1.pdf 
- pn532 user manual https://www.nxp.com/docs/en/user-guide/141520.pdf
- elechouse pn532 devboard manual https://1drv.ms/b/s!AhVEXR9ZKK8pg-kw3DkA_dTuov1nug?e=BMLYho
