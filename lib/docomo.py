# -*- coding: utf-8 -*-
import os
import requests
import json

class Docomo:
	def __init__(self, APIKEY):
		self.APIKEY = APIKEY

	def talk(self, message, path="./cache/audio/"):

		if not os.path.isfile(path+message+".wav"):
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
			print(r.status_code)
			wav = r.content
			with open(path+message+".wav","wb") as fout:
				fout.write(wav)
		char = "aplay {}{}.wav".format(path, message)
		os.system(char)

if __name__ == '__main__':
	APIKEY = ""
	docomo = Docomo(APIKEY)
	docomo.talk("テストです", "./")