from Drivers.Driver import Driver
from Drivers import EPS
import asyncio
import smbus
import RPi.GPIO as GPIO
import time

class BoomDeployer(Driver):
	def __init__(self):
		"""
		Calls parent constructor, Defines initial burn time, time to wait in between burns,
		and how many times to burn before giving up.  Sets up the GPIO pin for use by the actuate method.
		"""
		#super().__init__("BoomDeployer")
		# Initial values
		self.burnTimeWC1 = 10
		self.burnTimeWC2 = 10
		self.waitTime = 10
		self.numTimes = 3
	#The duty cycles will specify the maximum duty cycle for the PWM for each wire burn
		self.dutyCycle1 = 15
		self.dutyCycle2 = 15

        # Set up the GPIO pins for use
		GPIO.setmode(GPIO.BCM)

        # First Wirecutter
	# BOARD 38 is GPIO 20
		self.wireCutter1_high1 = 20
	# BOARD 36 is GPIO 16
		self.wireCutter1_high2 = 16
	# BOARD 7 is GPIO 4
		self.wireCutter1_low1 = 4

	# Set up Wirecutter 1 pins
		GPIO.setup(self.wireCutter1_high1, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.wireCutter1_high2,GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.wireCutter1_low1,GPIO.OUT, initial=GPIO.HIGH)
		self.PWM1 = GPIO.PWM(self.wireCutter1_high1, 500)

		#Second Wirecutter
	# BOARD 37 is GPIO 26
		self.wireCutter2_high1 = 26
	# BOARD 35 is GPIO 19
		self.wireCutter2_high2 = 19
	# BOARD 29 is GPIO 5
		self.wireCutter2_low1 = 5

	# Set up Wirecutter 2 pins
		GPIO.setup(self.wireCutter2_high1, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.wireCutter2_high2,GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.wireCutter2_low1,GPIO.OUT, initial=GPIO.HIGH)
		self.PWM2 = GPIO.PWM(self.wireCutter2_high1, 500)
	
	#used to turn on the eps bus
		self.Bus = EPS()

	async def deploy(self):
		"""
		Loop a specified number of times, setting the correct GPIO pins to HIGH/LOW  to start/stop
		the burn. Wait and then repeat with the other wirecutter mechanism.
		Note: PWM is used on only one channel.
		"""
		#this is turn onthe raw out put on the bus, this is incase it turns off 
		try:
			self.Bus.enableRaw()
		except: 
			pass

		for num in range(0, self.numTimes):
			#Turn on Wire Cutter 1
			#GPIO.output(self.wireCutter1_high1, GPIO.HIGH)
			GPIO.output(self.wireCutter1_high2, GPIO.HIGH)
			GPIO.output(self.wireCutter1_low1, GPIO.LOW)
			self.PWM1.start(0)

			for dc in range(0, self.dutyCycle1, 5):
				self.PWM1.ChangeDutyCycle(dc)
				time.sleep(0.05)

			#Burn for set number of seconds
			await asyncio.sleep(self.burnTimeWC1)
			self.PWM1.stop()

			#Turn off Wire Cutter 1
			GPIO.output(self.wireCutter1_high1, GPIO.LOW)
			GPIO.output(self.wireCutter1_high2, GPIO.LOW)
			GPIO.output(self.wireCutter1_low1, GPIO.HIGH)
			#Wait
			await asyncio.sleep(self.waitTime)

			#Turn on Wire Cutter 2
			#GPIO.output(self.wireCutter2_high1, GPIO.HIGH)
			GPIO.output(self.wireCutter2_high2, GPIO.HIGH)
			GPIO.output(self.wireCutter2_low1, GPIO.LOW)
			self.PWM2.start(0)

			for dc in range(0, self.dutyCycle2, 5):
				self.PWM2.ChangeDutyCycle(dc)
				time.sleep(0.05)

			#Burn for set number of seconds
			await asyncio.sleep(self.burnTimeWC2)
			self.PWM2.stop()

			#Turn off Wire Cutter 2
			GPIO.output(self.wireCutter2_high1, GPIO.LOW)
			GPIO.output(self.wireCutter2_high2, GPIO.LOW)
			GPIO.output(self.wireCutter2_low1, GPIO.HIGH)
			#Wait
			await asyncio.sleep(self.waitTime)

		print('Loop executed once')

	def read(self):
		"""
		Left undefined as no data is collected by this component
		"""
		pass
