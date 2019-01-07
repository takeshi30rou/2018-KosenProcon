# coding:utf-8 
import time
import RPi.GPIO as GPIO


def button():
	left = 20
	right = 21
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(left, GPIO.IN)
	GPIO.setup(right, GPIO.IN)

	GPIO.add_event_detect(right, GPIO.RISING)  # add rising edge detection on a channel
	GPIO.add_event_detect(left, GPIO.RISING)  #for both buttons

	start = time.time()
	while True:
		if GPIO.event_detected(right):
			GPIO.cleanup()
			return True
		if GPIO.event_detected(left):
			GPIO.cleanup()
			return False
		if time.time() - start > 5:
			GPIO.cleanup()
			return False
		time.sleep(0.001)

if __name__ == '__main__':
	r = button()
	print(r)