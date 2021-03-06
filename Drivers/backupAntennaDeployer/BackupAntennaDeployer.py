from asyncio.tasks import wait
from Drivers.Driver import Driver
import asyncio
import time
import RPi.GPIO as GPIO

class BackupAntennaDeployer(Driver):
    def __init__(self):
        """
        Calls parent constructor, sets burn time, sets GPIO pins
        """
        super().__init__("BackupAntennaDeployer")
        # Initial values
        self.burnTime = 10

        # Set up the GPIO pins for use
        GPIO.setmode(GPIO.BCM)

        # Setup GPIO pins
        # Primary Backup Pin: BOARD 33 which is GPIO 13
        self.primaryPin = 13
        # Secondary Backup Pin: BOARD 32 which is GPIO 12
        self.secondaryPin = 12
        GPIO.setup(self.primaryPin,GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.secondaryPin,GPIO.OUT, initial=GPIO.LOW)

    async def deployPrimary(self):
        """
        Set primary deploy pin to high for a specified time, triggering the
        backup antenna burn.
        """
        #Burn primary backup, then turn off and wait
        self.PWMPRIMARY = GPIO.PWM(self.primaryPin, 500)
        self.PWMPRIMARY.start(0)
        try:
            while True:

                for dc in range(0, 101, 5):
                    self.PWMPRIMARY.ChangeDutyCycle(dc)
                    time.sleep(0.05)
                await asyncio.sleep(self.burnTime)

                GPIO.output(self.primaryPin, GPIO.LOW)
                self.PWMPRIMARY.stop()
                
                break
        except:
            print("Failed to use primary antenna deploy")

        # GPIO.output(self.primaryPin, GPIO.HIGH)
        # time.sleep()
        # await asyncio.sleep(self.burnTime)
        # GPIO.output(self.primaryPin, GPIO.LOW)

    async def deploySecondary(self):
        """
        Set secondary deploy pin to high for a specified time, triggering the
        backup antenna burn.
        """

        self.PWMSECONDARY = GPIO.PWM(self.secondaryPin, 500)
        self.PWMSECONDARY.start(0)
        try:
            while True:

                for dc in range(0, 101, 5):
                    self.PWMSECONDARY.ChangeDutyCycle(dc)
                    time.sleep(0.05)
                await asyncio.sleep(self.burnTime)
                
                GPIO.output(self.secondaryPin, GPIO.LOW)
                self.PWMSECONDARY.stop()
                
                break
        except:
            print("Failed to use secondary antenna deploy")


        # GPIO.output(self.secondaryPin, GPIO.HIGH)
        # await asyncio.sleep(self.burnTime)
        # GPIO.output(self.secondaryPin, GPIO.LOW)

    def read(self):
        """
        Left undefined as no data is collected by this component
        """
        pass
