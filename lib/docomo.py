# -*- coding: utf-8 -*-
import os
import requests
import json
import time

#docomoの音声合成を使うためのライブラリ
class Docomo:
	def __init__(self, APIKEY):
		self.APIKEY = APIKEY

	#引数で指定した文字列を再生する
	def talk(self, message, path="./cache/audio/"):

		if not os.path.isfile(path+message+".wav"): #"既に音声ファイルがあるかどうかを確認する"
			url = 'https://api.apigw.smt.docomo.ne.jp/crayon/v1/textToSpeech?APIKEY='+self.APIKEY

			params = {
			  "Command":"AP_Synth",
			  "SpeakerID":"1",
			  "StyleID":"1",
			  "SpeechRate":"1.15",
			  "AudioFileFormat":"2",
			  "TextData":message
			}

			r = requests.post(url, data=json.dumps(params))
			if r.status_code == requests.codes.ok:
				wav = r.content
				with open(path+message+".wav","wb") as fout:
					fout.write(wav)

		if os.path.isfile(path+message+".wav"): #APIでエラーが発生し、音声ファイルが生成されないときのため
			char = "aplay {}{}.wav".format(path, message)
			os.system(char)

	#関数を実行したときの時刻を再生する
	def talk_clock(self, path="./cache/audio/"):
		hour_minute= time.strftime('ただいま%H:%Mです')
		self.talk(hour_minute, path)

if __name__ == '__main__':
	import sys
	sys.path.append("/home/pi/2018-KosenProcon/")
	from apikey import *
	docomo = Docomo(DOCOMOAPI)
	docomo.talk_clock("./")