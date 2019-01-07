# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from lib import button
from lib import heartRate
import os
import sys
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

#表情認識の為の処理
def emotion(personId,HR):
	my_opencv.video_capture()
	url = "http://10.12.156.150:8000/emotion"
	file = "./cache/video.avi"
	try:
		r = requests.post(url, data=open(file, "rb"), timeout=10)
		return r
	except:
		print("Failure")
		1/0

# def ini():
# 	right = 21
# 	GPIO.setmode(GPIO.BCM)
# 	GPIO.setup(right, GPIO.IN)
# 	GPIO.wait_for_edge(right, GPIO.RISING)
# 	GPIO.cleanup()

# ini()
# print(button.button())

try:

	docomo.talk("処理を開始します")
	docomo.talk("カメラを見てください。個人を特定します")

	my_opencv.face_tracking()
	result = id.identification()
	if result[0]:
		name = db.get_name(result[1])

		message="{}{}さん、こんにちは".format(name["last_kana"],name["first_kana"])
		docomo.talk(message)
		docomo.talk("脈拍を測定します。指をセンサーにおいてください。")
		HR = heartRate.heartRate()
		print("脈拍"+str(HR))


		docomo.talk("カメラを見てください。表情認識を行います")
		r = emotion(result[1],HR)

		docomo.talk("以下の内容で登録しますか？")

		print("---------------------------------------------------------")
		print("{}{}".format(name["last_kana"],name["first_kana"]))
		print("脈拍"+str(HR))
		print("{}".format(json.dumps(r.json(),indent=4)))
		print("---------------------------------------------------------")

		while True:
			YN = input("yes/no: ")
			if YN == "no":
				docomo.talk("初めからやり直してください。")
				sys.exit()
			elif YN == "yes":
				break
			else:
				print("yesかnoで入力してください")

		db.emotion3(r.json(),result[1],str(HR))

		docomo.talk("すべての処理が完了しました。ありがとうございます。")

	else:
		docomo.talk(result[1])

except Exception as e:
	docomo.talk("エラーが発生しました。終了します")
	raise(e)

