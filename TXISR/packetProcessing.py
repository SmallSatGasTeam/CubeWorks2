
# This file will be used to process the packets that are received from the ground. Before the packets reach this file, they will be sent to the radio and then over UART to the pi.
# The pythonInterrupt.py file monitors the UART buffer, and when data is received it will gather the data byte by byte and then parse the data for the header and footer that should be located on either end of our packets.
# The header and footer is the Hex representation of 'GASPACS'. The pythonInterrupt.py takes the packet data located in between the header and footer and then calls the processPacket() method located in this file, passing in an argument containing the packet data.
# processPacket() will convert the packet data to binary, and then go through bit by bit and perform the functionality specified in the packet.

import hashlib
import sys
sys.path.append('../')
import time
import os.path
from os import system
from Drivers.camera import Camera
import Drivers.boomDeployer as boomDeployer
import Drivers.transceiverConfig as transceiverConfig
import smbus
import hmac
from protectionProticol.fileProtection import FileReset
from TXISR.transmitionQueue import Queue
from flightLogic.missionModes.transmitting import Transmitting
import subprocess
import asyncio
import linecache
import os
import shutil

fileChecker = FileReset()
windows = Queue('/home/pi/TXISRData/txWindows.txt')
#These file paths are slightly different from the ones in transmitting.py

class packetProcessing:
	def __init__(self, transmitObject, cam):
		self.__cam = cam
		self.__bootRecordsPath = ("/home/pi/flightLogicData/bootRecords.txt")
		self.__filePaths = ["/home/pi/CubeWorks0/TXISR/", "/home/pi/CubeWorks1/TXISR/", "/home/pi/CubeWorks2/TXISR/", "/home/pi/CubeWorks3/TXISR/", "/home/pi/CubeWorks4/TXISR/"]
		self.__transmit = transmitObject

	async def processPacket(self, packetData):
		print('Processing packet')
		# Packet data comes in as hex, need to convet to binary to parse
		binaryDataLength = len(packetData) * 4
		print('bin data len' + str(binaryDataLength))
		binaryData = format(int(packetData,16), 'b').zfill(binaryDataLength)
		secretKey = b'SECRETKEY'

		if binaryData[0:8] == '00000000':
			# This is a TX Schedule packet.
			print("TX Schedule Packet")

			# Get window start delta T
			windowStartBinary = binaryData[8:40]
			windowStartDecimal = int(windowStartBinary,2)
			print("Window start in seconds: ", windowStartDecimal)

			# Get window duration
			windowDurationBinary = binaryData[40:56]
			windowDurationDecimal = int(windowDurationBinary,2)
			print("Window duration in seconds: ", windowDurationDecimal)

			# Get data type
			dataTypeBinary = binaryData[56:64]
			dataTypeDecimal = int(dataTypeBinary,2)
			print("Data type: ", dataTypeDecimal)

			# Get picture number
			pictureNumberBinary = binaryData[64:80]
			pictureNumberDecimal = int(pictureNumberBinary,2)
			print("Picture number: ", pictureNumberDecimal)

			#Get index
			print("index will be:", int(binaryData[80:112], 2))
			if int(binaryData[80:112], 2) == 0:
				index = -1
			else:
				index = int(binaryData[80:112], 2)
			print("Indexing to:", index)

			# Get the appended hash - it is a 16 byte (128 bit) value
			receivedHash = binaryData[112:]
			print("Received Hash: ", receivedHash)

			# Generated hash from received data
			generatedHash = hmac.new(secretKey, bytes(binaryData[0:112], 'utf-8'), digestmod=hashlib.md5)
			generatedHashHex = generatedHash.hexdigest()
			generatedHashLength = len(generatedHashHex) * 4
			generatedHashBinary = format(int(generatedHashHex,16), 'b').zfill(generatedHashLength)
			print("Generated hash: ", generatedHashBinary)
			if receivedHash == generatedHashBinary:
				print("Hashes match! Writing window")
				self.writeTXWindow(windowStartDecimal, windowDurationDecimal, dataTypeDecimal, pictureNumberDecimal, index)

			else:
				print("Hashes do not match, will not save window!")
		else:
			# This is a command packet
			print("Command packet")

			# Validate HMAC Hash
			# Note, hash is 16 bytes (128 bits). Command packet is 1 byte (8 bits)
			receivedHash = binaryData[-128:]
			print("Received Hash: ", receivedHash)

			# Generated hash from received data
			generatedHash = hmac.new(secretKey, bytes(binaryData[0:-128], 'utf-8'), digestmod=hashlib.md5)
			generatedHashHex = generatedHash.hexdigest()
			generatedHashLength = len(generatedHashHex) * 4
			generatedHashBinary = format(int(generatedHashHex,16), 'b').zfill(generatedHashLength)
			print("Generated hash: ", generatedHashBinary)
			if receivedHash == generatedHashBinary:
				print("Hashes match! Executing commands")

				if binaryData[8:16] == '00000000':
					# Turn off Transmitter
					print("Turn off Transmissions")
					self.disableTransmissions()
				else:
					#Turn on Transmitter
					print("Turn on Transmitter")
					self.enableTransmissions()

				if binaryData[16:24] == '00000000':
					# DO NOT Clear TX Schedule and Progress
					print("Do NOT Clear TX Schedule and Progress")
				else:
					# Clear TX Schedule & Progress
					print("Clear TX Schedule and Progress")
					self.clearTXFile()
					self.clearTXProgress()

				if binaryData[24:32] == '00000000':
					# Do not take picture
					print("Do not take picture")
				else:
					# Take picture
					print("Take picture")
					self.__cam.takePicture()

				if binaryData[32:40] == '00000000':
					# Do not deploy boom
					print("Do not deploy boom")
				else:
					# Deploy boom
					print("Deploy boom")
					deployer = boomDeployer.BoomDeployer()
					await deployer.deploy()

				if binaryData[40:48] == '00000000':
					# Do not reboot
					print("Do not reboot")
				else:
					#Send reboot command to Beetle
					print("Reboot")
					os.system("sudo reboot")

				fileChecker.checkFile(self.__bootRecordsPath)
				reboots = int(linecache.getline(self.__bootRecordsPath, 1))
				skip = int(linecache.getline(self.__bootRecordsPath, 3))
				linecache.clearcache()
				if skip != 4:
					if binaryData[56:64] == '00000000':
						#Chose whether or not to skip to post boom deploy
						print("Running flight logic normally.")
					else:
						print("Skipping to post boom deploy.")
						bootRecords = open(self.__bootRecordsPath, 'w+')
						bootRecords.write(str(reboots) + "\n1\n4\n")
						bootRecords.close()
						os.system("sudo reboot")

				if binaryData[64:72] == '00000000':
					# Keep Pictures
					print("Keeping Pictures")
				else:
					#Delete Pictures
					print("Deleting Pictures")
					self.deletePictures()

				if binaryData[72:80] == '00000000':
					# Keep Data
					print("Keeping Data")
				else:
					# Delete Data
					print("Deleting Data")
					self.deleteData()
				
				#Beacon commands have been removed and now send directly to the transceiver
					
			else:
				print("Hashes do not match, will not execute commands!")


	def writeTXWindow(self, windowStart, windowDuration, dataType, pictureNumber, index):
		# This function will write the TX window packet information to a file. Pass in the window start (delta T), window duration, data type, picture number, and Start From Beginning (1/0).
		# Note that this function saves the window start as an actual time, not a delta T - this is critical.

		# Convert window start from delta T to seconds since epoch
		windowStartTime = windowStart + int(time.time())
		print("Current time: ", int(time.time()))
		print("Start time: ", windowStartTime)
		
		fileChecker.checkFile("/home/pi/TXISRData/txWindows.txt")
		TXWindow_File = open("/home/pi/TXISRData/txWindows.txt", "a+")
		
		#write the data to the file, using the new queue
		txWindow = ( str(windowStartTime) + ',' + str(windowDuration) + ','
						+ str(dataType) + ',' + str(pictureNumber) + ','
						+ str(index) + '\n')
		windows.enqueue(txWindow)
			
		# close file
		TXWindow_File.close()
		
	def disableTransmissions(self):
		# This function will set a flag that will disable the radio transmissions. We will check the flag before making any transmissions.
		fileChecker.checkFile("/home/pi/TXISRData/transmissionFlag.txt")
		transmissionFlag_File = open("/home/pi/TXISRData/transmissionFlag.txt", "w")
		
		# write the data to the file,
		transmissionFlag_File.write("Disabled")
		
		# close the file
		transmissionFlag_File.close()
		
	def enableTransmissions(self):
		fileChecker.checkFile("/home/pi/TXISRData/transmissionFlag.txt")
		# This function will set a flag that will disable the radio transmissions. We will check the flag before making any transmissions.
		transmissionFlag_File = open("/home/pi/TXISRData/transmissionFlag.txt", "w")
		
		# write the data to the file,
		transmissionFlag_File.write("Enabled")
		
		# close file
		transmissionFlag_File.close()
		
	def clearTXFile(self):
		fileChecker.checkFile("/home/pi/TXISRData/txWindows.txt")
		# This function clears the TX windows file
		transmissionFlag_File = open("/home/pi/TXISRData/txWindows.txt", "w")
		
		# close file
		transmissionFlag_File.close()
		
	def clearTXProgress(self):
		fileChecker.checkFile("/home/pi/TXISRData/flagsFile.txt")
		# This function will clear the file that saves which timestamp has been transmitted most recently for each data type
		progressFile = open("/home/pi/TXISRData/flagsFile.txt", "w")
		progressFile.write('0\n')
		progressFile.write('0\n')
		progressFile.write('0\n')
		progressFile.write('0\n')
		progressFile.write('0\n')
	
	def deletePictures(self):
		os.system("cd ../../flightLogicData/; sudo rm -rf Pictures")

	def deleteData(self):
		os.system("cd ../../flightLogicData/; sudo rm Attitude_Data.txt Deploy_Data.txt TTNC_Data.txt")

