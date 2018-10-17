# -*- coding: utf-8 -*-
'''
初期化、顔認識、個人認識、画面表示を行うソース
'''
import os
import time
import requests
import json
import concurrent.futures

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

db.display_status_update("authentication",0) #認証情報をリセットしておく
db.currentUser_update("") #認証情報をリセットしておく
db.display_status_update("everything",1) #displayをリセットしておく
db.display_status_update("analysis_end",0)

#表情認識の為の処理
def emotion(personId):
	my_opencv.video_capture()
	url = "http://10.12.156.150:8000/emotion"
	file = "./cache/video.avi"
	try:
		r = requests.post(url, data=open(file, "rb"), timeout=10)
		print("{}".format(json.dumps(r.json(),indent=4)))
		db.emotion(r.json(), personId)
		print(r.json())
	except:
		print("Failure")
	finally:
		db.display_status_update("analysis_end",1)

#時報と天気を再生する
def welcome(message):
	docomo.talk(message)
	#時報
	if db.display_status_check("sound_time") == "1":
		docomo.talk_clock()

	#天気
	if db.display_status_check("sound_weather") == "1":
		weather=db.weather_check()
		docomo.talk("{}の天気は{},気温は{}℃です。".format(weather["place"],weather["weather"],weather["temperature"]))

#mainループ
while True:
	my_opencv.face_tracking()
	result = id.identification(display_status=True)
	db.display_status_update("everything",1)
	if result[0]:
		db.currentUser_update(result[1])
		name = db.get_name(result[1])

		message="{}{}さん、こんにちは".format(name["last_kana"],name["first_kana"])
		executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
		
		if not "guest" == result[1]:
			executor.submit(emotion,result[1])
		executor.submit(welcome,message)
		db.display_status_update("authentication",1)

		while True:
			
			#認証状態
			if not my_opencv.face_tracking(timeout=15):
				docomo.talk("さようなら")
				db.display_status_update("authentication",0)
				db.currentUser_update("")
				db.display_status_update("analysis_end",0)
				break
	else:
		docomo.talk(result[1])
	
	time.sleep(5)