# -*- coding: utf-8 -*-

import cv2
import sys
import time
import datetime
import os
import copy
face_image_path = "./cache/face_image.jpg"
video_path = "./cache/video.avi"

import sys,os
sys.path.append("/home/pi/2018-KosenProcon/lib")

from db import DB #データベースを使うためのライブラリ
db = DB()

class My_OpenCV:
	def __init__(self, cascade_path):
		self.c = cv2.VideoCapture(0)
		self.cascade = cv2.CascadeClassifier(cascade_path)
		if not self.c.isOpened():
			print("カメラとの接続に失敗しました")
			sys.exit()
		
	#顔を四角で囲む
	def infomation(self, image, facerect):
		color = (255, 255, 255)
		for rect in facerect:
			rect =rect*2
			cv2.rectangle(image, tuple(rect[0:2]),tuple(rect[0:2]+rect[2:4]), color, thickness=2)#検出した顔を囲む矩形の作成
		image = cv2.flip(image, 1)#反転
		cv2.imshow("face", image)
		cv2.waitKey(1)

	def detection(self):
		sum_of_detection = 0
		start = time.time()
		while sum_of_detection<10 and (time.time()-start)<2:
			r, image = self.c.read()
			face_image = copy.deepcopy(image)#保存用に値渡しを行う
			image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)#処理高速化のために1/4にリサイズする
			image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#グレースケール変換
			facerect = self.cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=1,minSize=(90, 90), maxSize=(100, 100))
			if self.display_status:
				self.infomation(face_image, facerect)
			else:
				cv2.destroyAllWindows()
			if len(facerect) > 0:
				sum_of_detection = sum_of_detection + 1
		self.face_image = face_image

	def face_tracking(self,timeout=None):
		initial_time = time.time()
		while True:
			if db.display_status_check("camera") == "1":
				self.display_status=True
			else:
				self.display_status=False
			start = time.time()
			self.detection()
			elapsed_time = time.time() - start
			if not timeout is None: #timeout処理
				if not time.time()-initial_time<timeout:
					return False
			if time.time()-initial_time>60: #自動消灯
				db.display_status_update("everything",0)
			if elapsed_time < 1:
				cv2.imwrite(face_image_path, self.face_image)
				return True	
				
	#表情認識ための表情を撮影する
	def video_capture(self, frame=50,display_status=False):
		fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
		video = cv2.VideoWriter(video_path, fourcc, 10.0, (640, 480))
		for i in range(1, frame):
			r, image = self.c.read()
			img = cv2.resize(image, (640,480))
			video.write(img)
			cv2.putText(img, str(i/10.0), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=2)
			if display_status:
				cv2.imshow("face",img)
			cv2.waitKey(1)

if __name__ == '__main__':
	path = "../haarcascade_frontalface_default.xml"
	mo = My_OpenCV(path)
	while(1):
		r = mo.face_tracking()
	# print(r)
	# mo.video_capture(frame=80)