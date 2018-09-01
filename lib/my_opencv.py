# -*- coding: utf-8 -*-

import cv2
import sys
import time

class My_OpenCV:
	def __init__(self, cascade_path):
		self.c = cv2.VideoCapture(0)
		if not self.c.isOpened():
			print("カメラとの接続に失敗しました")
			sys.exit()

		self.cascade = cv2.CascadeClassifier(cascade_path)

	def infomation(self, image, facerect):
		color = (255, 255, 255)
		for rect in facerect:
			cv2.rectangle(image, tuple(rect[0:2]),tuple(rect[0:2]+rect[2:4]), color, thickness=2)#検出した顔を囲む矩形の作成
		image = cv2.flip(image, 1)#反転
		cv2.imshow("face", image)
		cv2.waitKey(1)

	def detection(self):
		sum_of_detection = 0
		start = time.time()
		while sum_of_detection<10 and (time.time()-start)<2:
			r, image = self.c.read()
			image = cv2.resize(image, None, fx = 0.5, fy = 0.5)#アスペクト比を維持してリサイズする
			
			image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#グレースケール変換
			facerect = self.cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=1, minSize=(50, 50), maxSize=(100, 100))

			#顔を囲む
			self.infomation(image, facerect)

			if len(facerect) > 2:
				sum_of_detection = sum_of_detection + 1
		self.image = image

	def face_tracking(self):
		while True:
			start = time.time()
			self.detection()
			elapsed_time = time.time() - start
			if elapsed_time < 1:
				cv2.imwrite("face_image.jpg", self.image)
				return True
			
if __name__ == '__main__':
	path = "../haarcascade_frontalface_default.xml"
	MO = My_OpenCV(path)
	r = MO.face_tracking()
	print(r)
