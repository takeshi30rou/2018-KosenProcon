# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from lib import button
from lib import heartRate
import os
import sys

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
def emotion(personId):
	my_opencv.video_capture()
	# url = "http://40.74.75.91:8000/emotion"
	# file = "./cache/video.avi"
	# try:
	# 	r = requests.post(url, data=open(file, "rb"), timeout=10)
	# 	print("{}".format(json.dumps(r.json(),indent=4)))
	# 	db.emotion(r.json(), personId)
	# 	print(r.json())
	# except:
	# 	print("Failure")
	# finally:
	# 	db.display_status_update("analysis_end",1)

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

	my_opencv.face_tracking()
	result = id.identification(display_status=True)
	if result[0]:
		name = db.get_name(result[1])
		if "guest" == result[1]:
			docomo.talk("エラーが発生しました。終了します")
			sys.exit()

		message="{}{}さん、こんにちは".format(name["last_kana"],name["first_kana"])
		docomo.talk(message)
		docomo.talk("脈拍を測定します。指をセンサーにおいてください。")
		r = heartRate.heartRate()
		docomo.talk("脈拍は")
		docomo.talk(str(r))
		docomo.talk("です")

		docomo.talk("カメラを見てください。表情認識を行います")
		emotion(result[1])

	else:
		docomo.talk(result[1])

except Exception as e:
	docomo.talk("エラーが発生しました。終了します")
	raise e