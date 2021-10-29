from Drivers.Driver import Driver
from os import popen

class CpuTemperature(Driver):
	# Maximum and minimum temperature values for the Pi
	min = 0.0
	max = 70.0

	def __init__(self):
		super().__init__(CpuTemperature)

	def read(self):
		try:
			temp = popen("vcgencmd measure_temp").readline()
			temp = float(temp.replace("temp="," ").replace("\'C"," ").replace("\n"," "))
			return temp
		except:
			return max + 10
