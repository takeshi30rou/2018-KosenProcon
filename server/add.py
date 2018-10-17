# -*- coding: utf-8 -*-
'''
外部サーバーで表情認識を行うためのソース
'''
from statistics import mode

import cv2
from keras.models import load_model
import numpy as np

from emotion.utils.datasets import get_labels
from emotion.utils.inference import detect_faces
from emotion.utils.inference import draw_text
from emotion.utils.inference import draw_bounding_box
from emotion.utils.inference import apply_offsets
from emotion.utils.inference import load_detection_model
from emotion.utils.preprocessor import preprocess_input

import falcon
import json
emotion_labels = get_labels('fer2013')

class emotion(object):

	def __init__(self):
		# parameters for loading data and images
		detection_model_path = './emotion//trained_models/detection_models/haarcascade_frontalface_default.xml'
		emotion_model_path = './emotion/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'

		self.face_detection = load_detection_model(detection_model_path)
		self.emotion_classifier = load_model(emotion_model_path, compile=False)

		# getting input model shapes for inference
		self.emotion_target_size = self.emotion_classifier.input_shape[1:3]
		# loading models

		# hyper-parameters for bounding boxes shape
		self.emotion_offsets = (20, 40)

	def plot(self, result):
		import matplotlib.pyplot as plt
		for i in range(7):
			plt.plot(result[i],label=emotion_labels[i])

		plt.ylabel('emotion prediction')
		plt.xlabel('video frame')
		plt.ylim([0,1])
		plt.legend(loc='upper left')
		plt.savefig('./emotion/prediction.png')
		plt.close()

	def  on_post(self, req, res):

		body = req.stream.read()
		with open("./emotion/video.avi", 'wb') as f:
			f.write(body)

		video = cv2.VideoCapture("./emotion/video.avi")

		r, image = video.read()
		result = [[],[],[],[],[],[],[]]

		while r:
			bgr_image = image
			gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
			rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
			faces = detect_faces(self.face_detection, gray_image)
			
			for face_coordinates in faces:

				x1, x2, y1, y2 = apply_offsets(face_coordinates, self.emotion_offsets)
				gray_face = gray_image[y1:y2, x1:x2]
				try:
					gray_face = cv2.resize(gray_face, (self.emotion_target_size))
				except:
					continue

				gray_face = preprocess_input(gray_face, True)
				gray_face = np.expand_dims(gray_face, 0)
				gray_face = np.expand_dims(gray_face, -1)
				emotion_prediction = self.emotion_classifier.predict(gray_face)

				for i in range(7):
					result[i].append(emotion_prediction[0][i])

			#フレームが存在すれば、fはTrue
			r, image = video.read()

		emotion.plot(result)

		if len(result) > 0:
			emotions = {}
			for i in range(7):
				emotions.update({emotion_labels[i]:float(np.sum(result[i]))})
			res_json = emotions

		else:
			res_json = [""]

		res.body = json.dumps(res_json, ensure_ascii=False)

		# The following line can be omitted because 200 is the default
		# status returned by the framework, but it is included here to
		# illustrate how this may be overridden as needed.
		res.status = falcon.HTTP_200

api = application = falcon.API()
emotion = emotion()
api.add_route('/emotion', emotion)