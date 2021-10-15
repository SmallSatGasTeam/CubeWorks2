# This is essentially a header file that contains basic functions used in multiple programs

from inspect import currentframe, getframeinfo
import struct

def float4tohex(num):
	#takes a 4 byte float, returns a hex representation of it
	try:
		if(str(hex(struct.unpack('<I', struct.pack('<f', num))[0]))[2:] != '0'):
			return str(hex(struct.unpack('<I', struct.pack('<f', num))[0]))[2:]
		else:
			return str('00000000')
	except Exception as e:
		print("Failure to convert num in float4tohex. Exception: ", e, getframeinfo(currentframe()).filename, getframeinfo(currentframe()).lineno)
		return str('00000000')

def int4tohex(num):
	#takes a 4 byte int, returns a hex representation of it
	try:
		return str(format(num, '08x'))[-8:]
	except Exception as e:
		print("Failure to convert num in int4tohex. Exception: ", e, getframeinfo(currentframe()).filename, getframeinfo(currentframe()).lineno)
		return str(format(0, '08x'))[-8:]

def int1tohex(num):
	#takes a 1 byte integer, returns a hex representation of it
	try:
		return str(format(num, '02x'))[-2:]
	except Exception as e:
		print("Failure to convert num in int1tohex Exception: ", e, getframeinfo(currentframe()).filename, getframeinfo(currentframe()).lineno)
		return str(format(0, '02x'))[-2:]

def int2tohex(num):
	#takes a 2 byte integer, returns a hex representation of it
	try:
		return str(format(num, '04x'))[-4:]
	except Exception as e:
		print("Failure to convert num in int2tohex. Exception: ", e, getframeinfo(currentframe()).filename, getframeinfo(currentframe()).lineno)
		return str(format(0, '04x'))[-4:]

def int8tohex(num):
	#takes an 8 byte integer, returns a hex representation of it
	try:
		return str(format(num, '016x'))[-16:]
	except Exception as e:
		print("Failure to convert num in int8tohex. Exception: ", e, getframeinfo(currentframe()).filename, getframeinfo(currentframe()).lineno)
		return str(format(0, '016x'))[-16:]

class unexpectedValue(Exception):
	print("Received unexpected value.", getframeinfo(currentframe()).filename, getframeinfo(currentframe()).lineno)
	pass