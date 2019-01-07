# -*- coding: utf-8 -*-

from mcp3208 import MCP3208
import time
import numpy as np
import RPi.GPIO as GPIO

def heartRate():
	pin = 2
	# GPIOピン番号の定義方法を設定する（BCM/BOARD）
	GPIO.setmode(GPIO.BCM)
	# 18番ピンを出力モードで初期化する
	GPIO.setup(pin, GPIO.OUT)

	adc = MCP3208()
	threshold = 2#V

	x = np.arange(0, 60, 1)
	y = np.zeros(x.shape[0])

	heart_rate_duration = np.zeros(10)

	y[x.shape[0]-1]
	start = time.time()

	GPIO.output(pin, False)

	while True:
		
		data = adc.read(0)*5/4095.0
		if data >= threshold:
			if y[x.shape[0]-2]<y[x.shape[0]-1] and y[x.shape[0]-1] > data:
				duration  =time.time() - start
				if duration >=60/150.0:
					heart_rate_duration = np.roll(heart_rate_duration, -1)
					heart_rate_duration[heart_rate_duration.shape[0]-1]=duration
					heart_rate = round(60/np.mean(heart_rate_duration), 1)
					sd = round(np.std(heart_rate_duration),4)#標準偏差
					if np.count_nonzero(heart_rate_duration) == heart_rate_duration.shape[0]:
						print("{}bpm : standard deviation {}".format(heart_rate, sd))
					if sd < 0.04:
						break
				start = time.time()

		y = np.roll(y, -1)
		y[x.shape[0]-1]=data
		
		time.sleep(0.001)

	GPIO.output(pin, True)
	# GPIOを解放
	GPIO.cleanup()
	
	return heart_rate


if __name__ == '__main__':
	r = heartRate()
	print(r)
