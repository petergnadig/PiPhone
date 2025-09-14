#!usr/bin/python3

import RPi.GPIO as GPIO
import time
import serial

def readSerial():
        rdata=''
        while ser.inWaiting() > 0:
                rdata += ser.read(ser.inWaiting())
                time.sleep (0.0001)
        return rdata

GPIO.setmode(GPIO.BOARD)

GP_DIL=13  #GPIO_27 Dial counter
GP_CNT=12  #GPIO_18 Dialer - high if dial
GP_RCV=15  #GPIO_22 Receiver - high if up
GP_DILL=16 #GPIO_23 Dial counter led
GP_CNTL=22 #GPIO_25 Dieler led
GP_RCVL=37 #GPIO_26 Receiver led
GP_MODON=7 #GPIO_04 ModemOnOff

GPIO.setup(GP_DIL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #Tarcsazas GP_18
GPIO.setup(GP_CNT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #Tarcsa szamlalo GP_27
GPIO.setup(GP_RCV, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #Kagylo fent GP_22
GPIO.setup(GP_DILL,GPIO.OUT)
GPIO.output(GP_DILL,GPIO.HIGH)
GPIO.setup(GP_CNTL,GPIO.OUT)
GPIO.output(GP_CNTL,GPIO.HIGH)
GPIO.setup(GP_RCVL,GPIO.OUT)
GPIO.output(GP_RCVL,GPIO.HIGH)

print "Serial Start"
ser = serial.Serial("/dev/ttyUSB0",115200)
ModemReset = "ATZ\r\n"
ModemLogin = "AT+CREG?\r\n"
ModemCall = "ATD"
ModemHang = "ATH\r\n"
ModemAnsw = "ATA\r\n"
ModemCaId = "AT+CLIP=1"

print "MODEM SWITCH ON"
GPIO.setup(GP_MODON,GPIO.OUT)
GPIO.output(GP_MODON,GPIO.LOW)
print "sleep 4"
time.sleep(4)
print "sleep end"
GPIO.output(GP_MODON,GPIO.HIGH)

print "Modem reset"
ser.write(ModemReset)
res=''
while ('OK' in res)==False:
	res=readSerial()
	if res>'':
		print(res)

print "Modem Login"
ser.write(ModemLogin)
res=''
while  ('CREG' in res)==False:
	res=readSerial()
	if res>'':
		print(res)

print ("Modem OK")

GPIO.output(GP_DILL,GPIO.LOW)
GPIO.output(GP_CNTL,GPIO.LOW)
GPIO.output(GP_RCVL,GPIO.LOW)


rcv=GPIO.input(GP_RCV)
prevrcv=rcv
print "START ",
if rcv==GPIO.HIGH:
	print "RECEIVER UP"
else:
	print "RECEIVER DOWN"


dialnumber=""
lastdialtime=time.time()

incall=False

try:
	while True:
		#ReadModemMessage
		res=readSerial()
		if (res!=''):
			print ("--- MODEM: "),
			print(res)
		#Receiver
		rcv=GPIO.input(GP_RCV)
		if  rcv!=prevrcv:
			if rcv==GPIO.HIGH:
				dialnumber=""
				print "RECEIVER UP"
			else:
				if incall==True:
					print "Hangup"
					dialnumber=""
					incall=False
					ser.write(ModemHang)
				print "RECEIVER DOWN"
			prevrcv=rcv
		#Dial
		prevdial=0
		cc=0
		start_low=time.time()
		start_high=start_low
		while GPIO.input(GP_DIL)==GPIO.HIGH and rcv==GPIO.HIGH and incall==False:
			dial=GPIO.input(GP_CNT)
			if prevdial!=dial:
				if dial==GPIO.LOW:
					start_low=time.time()
					high=start_low-start_high
					##print "High:",
					##print high
				else:
					start_high=time.time()
					low=start_high-start_low
					##print "Low:",
					##print low,
					if low<0.1 and low>0.001:
						cc=cc+1
					##print "   Count:",
					##print cc
				prevdial=dial
				GPIO.output(GP_DILL,GPIO.input(GP_DIL))
				GPIO.output(GP_CNTL,GPIO.input(GP_CNT))
				GPIO.output(GP_RCVL,GPIO.input(GP_RCV))
		if cc>0:
			if cc>9:
				cc=0
			print
			dialnumber=dialnumber+str(cc)
			print "Dial:",
			print(dialnumber)
			lastdialtime=time.time()
		#CALL
		if time.time()-lastdialtime>3 and dialnumber>"" and incall==False:
			if dialnumber.startswith("111"):
				dialnumber="302505646"
			if dialnumber.startswith("112"):
				dialnumber="305905434"
			if dialnumber.startswith("06"):
				dialnumber="0036"+dialnumber[2:]
			if dialnumber.startswith("00")==False:
				dialnumber="0036"+dialnumber
			ModemDial="ATD"+dialnumber+";\r\n"
			print "START CALL:",
			print (ModemDial)
			incall=True
			ser.write(ModemDial)
		#Transfer input to led
		GPIO.output(GP_DILL,GPIO.input(GP_DIL))
		GPIO.output(GP_CNTL,GPIO.input(GP_CNT))
		GPIO.output(GP_RCVL,GPIO.input(GP_RCV))
except KeyboardInterrupt:
	GPIO.cleanup()
