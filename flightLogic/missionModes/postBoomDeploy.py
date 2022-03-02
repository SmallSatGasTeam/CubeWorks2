import sys
sys.path.append('../../')
import uasyncio
from flightLogic.missionModes.heartBeat import heart_beat

# TODO: ----- needs MicroPython rewrite -----

# from flightLogic.getDriverData import *
# from TXISR import pythonInterrupt

# safeModeObject was deleted below in the init parameters after saveObject
class postBoomMode:
	def __init__(self, saveObject, transmitObject, packetObj):
		self.__transmit = transmitObject
		self.__heartBeatObj = heart_beat()
		self.__tasks = [] # List will be populated with all background tasks
		# self.__safeMode = safeModeObject
		print("Initialized postBoomDeploy")
		self.__packet = packetObj

		# TODO: ----- needs MicroPython rewrite -----

		# self.__getTTNCData = TTNCData(saveObject)
		# self.__getAttitudeData =  AttitudeData(saveObject)

	async def run(self):
		#Set up background processes
		print("Inside of run in postBoomDeploy")
		self.__tasks.append(uasyncio.create_task(self.__heartBeatObj.heartBeatRun()))

		# TODO: ----- needs MicroPython rewrite -----
		# self.__tasks.append(asyncio.create_task(pythonInterrupt.interrupt(self.__transmit, self.__packet)))
		# self.__tasks.append(asyncio.create_task(self.__getTTNCData.collectTTNCData(4))) #Post-boom is mode 4
		# self.__tasks.append(asyncio.create_task(self.__getAttitudeData.collectAttitudeData()))

		print("Initalized all tasks.")
		while True:
			# Don't remove this print statement, the while loop is an integral part
			# of making sure that postBoomDeploy doesn't crash and it needs to
			# have something in there so it doesn't crash and suffer
			print('This is post Boom Deploy')
			await uasyncio.sleep(10)	

	# TODO: Check if this works in MicroPython
	def cancellAllTasks(self, taskList): #Isn't used in this class, but here anyways
		try:
			for t in taskList:
				t.cancel()
		except uasyncio.exceptions.CancelledException:
			print("Caught thrown exception in cancelling background task")
