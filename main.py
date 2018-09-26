# -*- coding: utf-8 -*-
import os
import time
import requests
import json

haarcascade_path = "./haarcascade_frontalface_default.xml" #カスケード分類器
BASE_URL = "https://westus.api.cognitive.microsoft.com/face/v1.0/" # westus regional Base URL
img_url = "./cache/face_image.jpg" #個人認識に使う写真
from apikey import * #apikeyを取り出す
from lib.docomo import Docomo #docomoAPIを使うためライブラリ
docomo = Docomo(DOCOMOAPI)
from lib.db import DB #データベースを使うためのライブラリ
db = DB()
from lib.my_opencv import My_OpenCV #OpenCVを使うためのライブラリ
my_opencv = My_OpenCV(haarcascade_path)
from lib.identification import Identification #個人認識を行うためのライブラリ
id = Identification(BASE_URL,FACEAPI,img_url)
# 必要なフォルダの存在を確認する
if not os.path.isdir("./cache"):
	os.system("mkdir ./cache")
	if not os.path.isdir("./cache/audio"):
		os.system("mkdir ./cache/audio")
# 必要なフォルダの存在を確認する
if not os.path.isdir("./face/"):
	os.system("mkdir "+"./face/")

# 評価式
def evaluation(happy,sad,neutral):
	y=0.000980305511429404+0.0222859331905098*happy-0.0225111298759341*sad+0.0000242095263100815*neutral
	return y

db.display_status_update("authentication",0) #認証情報をリセットしておく

###表情認識の為の処理
def emotion(personId):
	docomo.talk("5秒間お待ちください")
	my_opencv.video_capture()

	docomo.talk("完了しました")
	url = "http://10.12.156.150:8000/emotion"
	file = "./cache/video.avi"
	r = requests.post(url, data=open(file, "rb"))

	print("{}".format(json.dumps(r.json(),indent=4)))
	db.emotion_2(r.json(), personId)

#mainループ
while True:
	my_opencv.face_tracking(display_status=True)
	result = id.identification(display_status=True)
	if result[0]:
		name = db.get_name(result[1])
		message="{}{}さま、こんにちは".format(name["last_kana"],name["first_kana"])
		docomo.talk(message)
		if not "guest" == result[1]:
			emotion(result[1])
		while True:
			db.display_status_update("authentication",1)
			#ここに画面の更新が入る
			if not my_opencv.face_tracking(timeout=10,display_status=True):
				docomo.talk("さようなら")
				db.display_status_update("authentication",0)
				break
	else:
		docomo.talk(result[1])
	
	time.sleep(5)
