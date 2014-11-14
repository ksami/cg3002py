from bmp180 import BMP085
import time

BMP085_STANDARD = 1
BMP085_I2CADDR = 0x77
SEA_LEVEL = 101325.0

if __name__ == "__main__":

	bmp = BMP085(BMP085_STANDARD, BMP085_I2CADDR, 1)

	while(True):
		print "Altitude:", bmp.read_altitude(SEA_LEVEL)
		time.sleep(1)