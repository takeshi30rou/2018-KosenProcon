# -*- coding: utf-8 -*-
import cognitive_face as CF
import urllib3
urllib3.disable_warnings()
import json


class Identification:
	def __init__(self,BASE_URL,FACEAPI,img_url):
		CF.Key.set(FACEAPI)
		CF.BaseUrl.set(BASE_URL)
		self.img_url = img_url
		self.display_status=False

	#結果をコンソールに表示する関数
	def display(self,text):
		if self.display_status:
			print("{}".format(json.dumps(text,indent=4)))

	#azure FaceAPIを使って個人認識を行う
	def identification(self,display_status=False):
		self.display_status = display_status #結果をdisplayするか
		detect_result = CF.face.detect(self.img_url,attributes="emotion") #個人認識を行うために、初めに顔認識を行う
		self.display(detect_result)

		if not str(detect_result) == "[]": #個人認識を行う
			faceIds = [detect_result[0]["faceId"]]
			if len(detect_result) == 1:
				identify_result = CF.face.identify(faceIds,"teamkatori")
				self.display(identify_result)

				if not str(identify_result[0]["candidates"]) == "[]":
					return True,identify_result[0]["candidates"][0]["personId"]
					
				else:
					return True,"guest"
			else:
				return False,"複数人を検知しました"
		else:
			return False,"顔を認識できませんでした"

if __name__ == '__main__':
	#apikeyを取り出す
	from apikey import *
	BASE_URL = "https://westus.api.cognitive.microsoft.com/face/v1.0/"
	img_url = '../face_image.jpg'
	id = Identification(BASE_URL,FACEAPI,img_url)
	personId = id.identification(display_status=True)
	print(personId)
