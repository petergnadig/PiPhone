#!usr/bin/python3

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup( 7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #Tarcsazas
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #Tarcsa szamlalo
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #Kagylo fent

GPIO.setup(15,GPIO.OUT)  # Telefonalas led
GPIO.output(15,0)
GPIO.setup(16,GPIO.OUT)  # Tarcsazas
GPIO.output(16,0)
GPIO.setup(18,GPIO.OUT)  # Kagylo led
GPIO.output(18,0)

global c
c=0

def dialstart(par):
	global c
	if GPIO.input(11)==GPIO.HIGH:
		print("DIAL!")
		c=0
	else:
		print("DIAL END!")
		print(c)

def count(par):
	global c
	c=c+1

GPIO.add_event_detect(11,GPIO.BOTH,callback=dialstart,bouncetime=1000)
GPIO.add_event_detect( 7,GPIO.RISING,callback=count,bouncetime=30)

try:
	while True:
		GPIO.output(16,GPIO.input( 7))
		GPIO.output(18,GPIO.input(13))
		GPIO.output(15,GPIO.input(11))
except KeyboardInterrupt:
	GPIO.cleanup()
