# -*- coding: utf-8 -*-
import cognitive_face as CF
import urllib3
urllib3.disable_warnings()
import json
import os
import time
import sys
import requests


#カスケード分類器
haarcascade_path = "./haarcascade_frontalface_default.xml"
# westus regional Base URL
BASE_URL = "https://westus.api.cognitive.microsoft.com/face/v1.0/"

#apikeyを取り出す
from apikey import *

CF.Key.set(FACEAPI)
CF.BaseUrl.set(BASE_URL)
from lib.docomo import Docomo
docomo = Docomo(DOCOMOAPI)
from lib.db import DB
db = DB()
from lib.my_opencv import My_OpenCV
my_opencv = My_OpenCV(haarcascade_path)

# 必要なフォルダの存在を確認する
if not os.path.isdir("./cache"):
	os.system("mkdir ./cache")
	if not os.path.isdir("./cache/audio"):
		os.system("mkdir ./cache/audio")
if not os.path.isdir("./face/"):
	os.system("mkdir "+"./face/")

def main_process():	
	# You can use this example JPG or replace the URL below with your own URL to a JPEG image.
	img_url = './face_image.jpg'
	#img_url ="http://www.mis.med.akita-u.ac.jp/~kata/image/originalsource/lenna.jpg" #lenna
	detect_result = CF.face.detect(img_url,attributes="emotion")
	print("{}".format(json.dumps(detect_result,indent=4)))
	#faceAPI_faceRectangle(detect_result)

	if not str(detect_result) == "[]":
		faceIds = [detect_result[0]["faceId"]]
		if len(detect_result) == 1:
			identify_result = CF.face.identify(faceIds,"teamkatori")
			print("{}".format(json.dumps(identify_result,indent=4))) 

			if not str(identify_result[0]["candidates"]) == "[]":
				#db.emotion_1(detect_result, identify_result[0]["candidates"][0]["personId"])
				name = db.get_name(identify_result[0]["candidates"][0]["personId"])

				message = name["last_kana"]+name["first_kana"]+"さん、こんにちは"
				docomo.talk(message)
				my_opencv.faceAPI_add_face(detect_result, identify_result)
				
				docomo.talk("5秒間お待ちください")
				# fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
				# video = cv2.VideoWriter('video.avi', fourcc, 10.0, (640, 480))
				# for i in range(1, 10*5):
				# 	r, image = c.read()
				# 	img = cv2.resize(image, (640,480))
				# 	video.write(img)
				# 	cv2.putText(img, str(i/10.0), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=2)
				# 	cv2.imshow("face",img)
				# 	cv2.waitKey(1)

				# docomo.talk("完了しました")
				# url = "http://10.12.156.150:8000/emotion"
				# file = "video.avi"
				# r = requests.post(url, data=open(file, "rb"))

				# print("{}".format(json.dumps(r.json(),indent=4)))
				# db.emotion_2(r.json(), identify_result[0]["candidates"][0]["personId"])
				time.sleep(2)

			else:
				faceAPI_add_face(detect_result, identify_result)
				docomo.talk("登録されていないユーザーです")
				time.sleep(2)


		else:
			docomo.talk("複数人を検知しました")
			time.sleep(2)

	else:
		print("顔を認識できませんでした")
		time.sleep(2)

while True:
	my_opencv.face_tracking()
	main_process()
