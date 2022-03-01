# pylint: disable=E,W,C,R
# type: ignore

import uasyncio
from machine import Pin

class heart_beat:
    __heartbeat_pin = 25
    __pin = None

    def __init__(self) -> None:
        print("Test")
        self.__pin = Pin(self.__heartbeat_pin, Pin.OUT)


    async def heartBeatRun(self): #Sets up up-and-down voltage on pin 40 (GPIO 21) for heartbeat with Arduino
        waitTime = 4
        while True:
            self.__pin.value(1)
            print("Heartbeat wave high")
            await uasyncio.sleep(waitTime/2)
            
            self.__pin.value(0)
            print("Heartbeat wave low")
            await uasyncio.sleep(waitTime/2)

# This will be called by the parent, but for testing...
heartBeat = heart_beat()
uasyncio.run(heartBeat.heartBeatRun())