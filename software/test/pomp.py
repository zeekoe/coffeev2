import smbus
import pigpio
import time
import os

globalpi = pigpio.pi()
globalpi.write(18,1)


def gpiopompcb(gpio, level, tick):
	print (gpio, level, tick)


globalpi.set_pull_up_down(31, pigpio.PUD_UP)
globalpi.callback(31, pigpio.EITHER_EDGE, gpiopompcb)

globalpi.write(18,1)
time.sleep(1)
globalpi.write(18,0)
time.sleep(1)
globalpi.write(18,1)
time.sleep(3)
globalpi.write(18,0)
time.sleep(1)
globalpi.write(18,1)
