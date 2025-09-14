#!/usr/bin/python
# Filename: text.py
import serial
import time
print ("Hello")
ser = serial.Serial("/dev/ttyUSB0",115200)
print (ser)


W_buf_reset = "ATZ\r\n"
W_buf_logoin = "AT+CREG?\r\n"
W_buf_phone =  "ATD0036302505646;\r\n"

def readSerial():
	rdata=''
	while ser.inWaiting() > 0:
        	rdata += ser.read(ser.inWaiting())
		time.sleep (0.0001)
	return rdata

ser.write(W_buf_reset)
print (W_buf_reset)
ser.write(W_buf_logoin)
print (W_buf_logoin)
ser.flushInput()

data=''

try:
	while True:
		data = readSerial()
		if data != '':
			print(data)
			if 'CREG' in data:
				print ("call phone")
				print (W_buf_phone)
				ser.write (W_buf_phone)
			data = ''
except KeyboardInterrupt:
	if ser != None:
		ser.close()
