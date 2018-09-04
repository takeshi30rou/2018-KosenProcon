# -*- coding: utf-8 -*-
import cognitive_face as CF
import urllib3
urllib3.disable_warnings()
import json
import os
import time
import cv2
import copy
import sys
import requests
import datetime

from lib.docomo import Docomo
from lib.db import DB

from apikey import *
CF.Key.set(FACEAPI)
docomo = Docomo(DOCOMOAPI)
db = DB()


haarcascade_path = "./haarcascade_frontalface_default.xml"
ignore_coordinates = []
tolerance = 0

# Replace with your regional Base URL
BASE_URL = "https://westus.api.cognitive.microsoft.com/face/v1.0/"  
CF.BaseUrl.set(BASE_URL)

if not os.path.isdir("./cache"):
	os.system("mkdir ./cache")
	if not os.path.isdir("./cache/audio"):
		os.system("mkdir ./cache/audio")

if not os.path.isdir("./face/"):
	os.system("mkdir "+"./face/")

c = cv2.VideoCapture(0)
if not c.isOpened():
	print("カメラとの接続に失敗しました")
	sys.exit()

def trimming(image):
	size = 400
	x = (640-size)//2
	y = (480-size)//2
	img = image[y:size+y,x:size+x]
	return img

#FaceAPIレスポンスのfaceRectangleで写真を切り取る
def faceAPI_add_face(detect_result, identify_result):
	
	today = datetime.date.today()

	now = datetime.datetime.today()
	time = datetime.time(now.hour,now.minute,now.second)

	if identify_result[0]["candidates"] == []:
		personId = "unknown"
	else:
		personId = identify_result[0]["candidates"][0]["personId"]

	if personId == "unknown":
		if not os.path.isdir("./face/"+"unknown"):
			os.system("mkdir "+"./face/"+"unknown")
	else:
		if not os.path.isdir("./face/"+personId):
			os.system("mkdir "+"./face/"+personId)
		if not os.path.isdir("./face/"+personId+"/"+str(today)):
			os.system("mkdir "+"./face/"+personId+"/"+str(today))
	
	left = detect_result[0]["faceRectangle"]["left"]
	top = detect_result[0]["faceRectangle"]["top"]
	width = detect_result[0]["faceRectangle"]["width"]
	height = detect_result[0]["faceRectangle"]["height"]

	if personId == "unknown":
		path ="./face/"+personId+"/"+str(time)+".jpg"
		face_image = cv2.imread('face_image.jpg')
		face_image = face_image[top:top+height,left:left+width]
		cv2.imwrite(path, face_image)
	else:
		path ="./face/"+personId+"/"+str(today)+"/"+str(time)+".jpg"
		face_image = cv2.imread('face_image.jpg')
		face_image = face_image[top:top+height,left:left+width]
		cv2.imwrite(path, face_image)

def openCV_track_face(ignore_coordinates):
	detect_lost = "initialize"
	time_sum = 0
	face_num = 0
	color = (255, 255, 255)
	swich_gui = True
	title = face_image = cv2.imread('title.png')
	#カスケード分類器の特徴量を取得する
	cascade = cv2.CascadeClassifier(haarcascade_path)
	while 1:
		start = time.time()
		

		r, image = c.read()

		#保存用に値渡しを行う
		face_image = copy.deepcopy(image)

		image = trimming(image)

		#アスペクト比を維持してリサイズする
		image = cv2.resize(image, None, fx = 0.5, fy = 0.5)

		image = cv2.flip(image, 1)

		#グレースケール変換
		image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		#物体認識（顔認識）の実行
		#image – CV_8U 型の行列．ここに格納されている画像中から物体が検出されます
		#objects – 矩形を要素とするベクトル．それぞれの矩形は，検出した物体を含みます
		#scaleFactor – 各画像スケールにおける縮小量を表します
		#minNeighbors – 物体候補となる矩形は，最低でもこの数だけの近傍矩形を含む必要があります
		#flags – このパラメータは，新しいカスケードでは利用されません．古いカスケードに対しては，cvHaarDetectObjects 関数の場合と同じ意味を持ちます
		#minSize – 物体が取り得る最小サイズ．これよりも小さい物体は無視されます
		facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=1, minSize=(50, 50), maxSize=(100, 100))
		#facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=3, minSize=(10, 10), flags = cv2.cv.CV_HAAR_SCALE_IMAGE)

		# ##アスペクト比を無視してリサイズする
		# image_gray = cv2.resize(image_gray,(250,250))
		# facerect_resize = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=1, minSize=(0, 0))
		new_facerect = []
		if not ignore_coordinates == []:
			if len(facerect) > 0:
				for rect in facerect:
					for ig_rect in ignore_coordinates:
						tolerance_points = 0
						for var in range(0,3):
							if rect[var] in range(ig_rect[var]-tolerance,ig_rect[var]+tolerance):
								tolerance_points += 1
						if tolerance_points == 0:
							new_facerect.append(rect)
			facerect = new_facerect

		if len(facerect) > 0:
			#顔の数をカウント
			face_num = face_num + 1
			for rect in facerect:
				#検出した顔を囲む矩形の作成
				cv2.rectangle(image, tuple(rect[0:2]),tuple(rect[0:2]+rect[2:4]), color, thickness=2)

		#一定の時間と顔計数で　detect処理をする
		if time_sum <8 and face_num >10:
			cv2.imwrite("face_image.jpg", face_image)
			detect_lost = "detect"
			face_num = 0
			time_sum = 0	

		#lost処理をする
		if time_sum >10:
			if face_num <11:
				detect_lost = "lost"
			face_num = 0
			time_sum = 0

		#顔認識にかかる時間を計測
		elapsed_time = time.time() - start
		time_sum = time_sum+elapsed_time

		key = cv2.waitKey(10)
		if key == 32:
			swich_gui = not(swich_gui)
		
		
		#無視される領域を描画する
		if len(ignore_coordinates) > 0:
			for rect in ignore_coordinates:
				cv2.rectangle(image, tuple(rect[0:2]),tuple(rect[0:2]+rect[2:4]), (0, 255, 0), thickness=2)

		#イメージを表示する
		cv2.putText(image, str(round(elapsed_time*1000))+"ms", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=2)
		cv2.putText(image, detect_lost, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=2)
		cv2.imshow("face", image)

		if detect_lost == "detect":
			return facerect

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
				faceAPI_add_face(detect_result, identify_result)
				
				docomo.talk("5秒間お待ちください")
				fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
				video = cv2.VideoWriter('video.avi', fourcc, 10.0, (640, 480))
				for i in range(1, 10*5):
					r, image = c.read()
					img = cv2.resize(image, (640,480))
					video.write(img)
					cv2.putText(img, str(i/10.0), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=2)
					cv2.imshow("face",img)
					cv2.waitKey(1)

				docomo.talk("完了しました")
				url = "http://10.12.156.150:8000/emotion"
				file = "video.avi"
				r = requests.post(url, data=open(file, "rb"))

				print("{}".format(json.dumps(r.json(),indent=4)))
				db.emotion_2(r.json(), identify_result[0]["candidates"][0]["personId"])
				time.sleep(1)

				return False
			
			else:
				faceAPI_add_face(detect_result, identify_result)
				docomo.talk("登録されていないユーザーです")
				time.sleep(1)
				return False

		else:
			docomo.talk("複数人を検知しました")
			time.sleep(1)
			return False
	else:
		print("顔を認識できませんでした")
		time.sleep(1)
		return True



# while True:
# 	face_coordinates = openCV_track_face(ignore_coordinates)
# 	print(face_coordinates)
# 	if main_process():
# 		ignore_coordinates = face_coordinates

