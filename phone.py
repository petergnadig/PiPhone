#!usr/bin/python


import RPi.GPIO as GPIO
import time
import serial
import datetime

def readSerial(timeout=1.0):
	rdatab = b""
	start_time = time.time()

	while ser.in_waiting > 0:
		rdatab += ser.read(ser.in_waiting)
		time.sleep(0.01)
	try:
		rdata = rdatab.decode("utf-8")
	except UnicodeDecodeError:
		rdata = rdatab.decode("utf-8", errors="replace")
	return rdata

def sendModem(command):
	com= command.encode('ascii')+b'\r\n'
	print("Modem command: ",com)
	ser.write(com)
	res=""
	dt0 = time.time()
	print()
	while res=="" and time.time()-dt0<1:
		res=readSerial()
		now = datetime.datetime.now()
		print(f"\033[F\033[{30}G ReadSerial",now)
	print("Modem answ: "),
	print(res)
	return(res)


print ("------------------ PROGRAM START ------------------")

GPIO.setmode(GPIO.BOARD)

GP_DIL=13  #GPIO_27 Dial counter
GP_CNT=12  #GPIO_18 Dialer - high if dial
GP_RCV=33  #GPIO_13 Receiver - high if up
GP_DILL=16 #GPIO_23 Dial counter led
GP_CNTL=22 #GPIO_25 Dieler led
GP_RCVL=37 #GPIO_26 Receiver led
GP_RING=32 #GPIO_12 Bell

GP_CALL=15 #GPIO_22 CallIn?
GP_MODON=40 #GPIO_04 ModemOnOff

GPIO.setup(GP_DIL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GP_CNT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GP_RCV, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GP_CALL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(GP_DILL,GPIO.OUT)
GPIO.output(GP_DILL,GPIO.HIGH)
GPIO.setup(GP_CNTL,GPIO.OUT)
GPIO.output(GP_CNTL,GPIO.HIGH)
GPIO.setup(GP_RCVL,GPIO.OUT)
GPIO.output(GP_RCVL,GPIO.HIGH)
GPIO.setup(GP_RING,GPIO.OUT)
GPIO.output(GP_RING,GPIO.LOW)
GPIO.setup(GP_MODON,GPIO.OUT)
GPIO.output(GP_MODON,GPIO.HIGH)


print ("------------------Serial Start------------------")
#ser = serial.Serial("/dev/ttyUSB0",115200)
ser = serial.Serial("/dev/ttyS0",115200)
ModemReset = "ATZ"
ModemLogin = "AT+CREG?"
ModemCall = "ATD"
ModemHang = "ATH"
ModemAnsw = "ATA"
ModemCaId = "AT+CLIP=1"


#try modem

res=""
count=4
while count>0 and  ("OK" in res or "ATZ" in res)==False:
	res=readSerial()
	print ("Modem reset:", 5-count)
	res=sendModem(ModemReset)
	if ("ATZ" in res)==False:
		print ("MODEM SWITCH ON")
		GPIO.setup(GP_MODON,GPIO.OUT)
		GPIO.output(GP_MODON,GPIO.LOW)
		time.sleep(6)
		print ("MODEM ON")
		GPIO.output(GP_MODON,GPIO.HIGH)
	else:
		print("Modem already on")
	count=count-1

#print "Modem reset"
#res=sendModem(ModemReset)

print ("Modem Login")
res=sendModem(ModemLogin)
while  ('+CREG:' in res)==False:
	res=readSerial()
	if res>'':
		print(res)

print ("Modem Show caller ID")
res=sendModem(ModemCaId)

print ("Modem OK")

GPIO.output(GP_DILL,GPIO.LOW)
GPIO.output(GP_CNTL,GPIO.LOW)
GPIO.output(GP_RCVL,GPIO.LOW)
GPIO.output(GP_RING,GPIO.LOW)

rcv=GPIO.input(GP_RCV)
prevrcv=rcv
print ("------------ START ")
if rcv==GPIO.HIGH:
	print ("RECEIVER UP")
else:
	print ("RECEIVER DOWN")
call=GPIO.input(GP_CALL)
prevcall=call

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
		if 'RING' in res:
			GPIO.output(GP_RING,GPIO.HIGH)
			time.sleep(0.5)
			GPIO.output(GP_RING,GPIO.LOW)
		#CALL?
		call=GPIO.input(GP_CALL)
		if  call!=prevcall:
			if call==GPIO.HIGH:
				print("---CALL SIGNAL HIGH---")
			else:
				print("---CALL SIGNAL LOW---")
			prevcall=call
		#Receiver
		rcv=GPIO.input(GP_RCV)
		if  rcv!=prevrcv:
			if rcv==GPIO.HIGH:
				dialnumber=""
				print ("RECEIVER UP")
				res=sendModem(ModemAnsw)
			else:
				print ("Hangup")
				dialnumber=""
				incall=False
				res=sendModem(ModemHang)
				res=sendModem(ModemReset)
				res=sendModem(ModemCaId)
				print ("RECEIVER DOWN")
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
			print ("Dial:"),
			print(dialnumber)
			lastdialtime=time.time()
		#CALL
		if time.time()-lastdialtime>3 and dialnumber>"" and incall==False:
			if dialnumber=="1":
				dialnumber="302505646"
			if dialnumber=="2":
				dialnumber="305905434"
			if dialnumber.startswith("06"):
				dialnumber="0036"+dialnumber[2:]
			if dialnumber.startswith("00")==False:
				dialnumber="0036"+dialnumber
			ModemDial="ATD"+dialnumber+"\r\n"
			print ("START CALL:"),
			print (ModemDial)
			incall=True
			res=sendModem(ModemDial)
		#Transfer input to led
		GPIO.output(GP_DILL,GPIO.input(GP_DIL))
		GPIO.output(GP_CNTL,GPIO.input(GP_CNT))
		GPIO.output(GP_RCVL,GPIO.input(GP_RCV))
		now = datetime.datetime.now()
		print(f"\033[F\033[{30}G InLoop",now)
except KeyboardInterrupt:
	GPIO.cleanup()
