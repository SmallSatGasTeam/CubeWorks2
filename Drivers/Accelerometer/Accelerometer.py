#Make sure the following libraries are installed:
#   sudo pip3 install RPI.GPIO
#   sudo pip3 install adafruit-blinka
#   sudo pip3 install adafruit-circuitpython-lsm303-accel
#   For LSM303AGR:
#     sudo pip3 install adafruit-circuitpython-lis2mdl
#   For LSM303DLH:
#     sudo pip3 install adafruit-circuitpython-lsm303dlh-mag

from Drivers.Driver import Driver
import board
import busio
import adafruit_lsm303_accel

"""
Pulls data from the Accelerometer
"""

class Accelerometer(Driver):
  #Set up I2C link
  i2c = busio.I2C(board.SCL, board.SDA)
    
  def __init__(self):
    super().__init__("Accelerometer")
    
  def read(self):
    accelMin = -16
    accelMax = 16
    returnDummy = False
    accel = adafruit_lsm303_accel.LSM303_Accel(self.i2c)
    try:
      accel.acceleration
    except:
      print("Failed to pull Accelerometer.")
      returnDummy = True
    #   print("Failed to pull Accelerometer. Exception: ", repr(e), 
    # getframeinfo(currentframe()).filename, getframeinfo(currentframe()).lineno)
    if returnDummy:
      accelX, accelY, accelZ = accelMax + 1, accelMax + 1, accelMax + 1
      return accelX, accelY, accelZ
    return accel.acceleration
