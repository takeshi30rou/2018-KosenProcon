# -*- coding: utf-8 -*-
import json
from os.path import join, relpath
from glob import glob
import cognitive_face as CF
import urllib3
urllib3.disable_warnings()
import pymysql.cursors
import sys
import os
import shutil
import time
from progressbar import ProgressBar
import collections

sys.path.append("/home/pi/2018-KosenProcon/")
from apikey import *
CF.Key.set(FACEAPI)
person_group_id = "teamkatori"

def add_personId(personId, last, first, last_kana, first_kana):
	# MySQLに接続する
	connection = pymysql.connect(host='localhost',
	                             user='pi',
	                             password='raspberry',
	                             db='katori',
	                             charset='utf8',
	                             # cursorclassを指定することで
	                             # Select結果をtupleではなくdictionaryで受け取れる
	                             cursorclass=pymysql.cursors.DictCursor)
	try:
		# Insert処理
		with connection.cursor() as cursor:
		    sql = "INSERT INTO personIds"\
		    "(personId, last, first, last_kana, first_kana)"\
		    "VALUES (%s, %s, %s, %s, %s)"
		    #print(sql)
		    r = cursor.execute(sql, (personId, last, first, last_kana, first_kana))
		    #print(r) # -> 1
		    # autocommitではないので、明示的にコミットする
		    connection.commit()
	finally:
		# MySQLから切断する
		connection.close()

def create():
	decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict) #jsonファイルの辞書を順番通りにload
	with open("/home/pi/2018-KosenProcon/cache/upload/target_info.json") as f: #target_info.jsonをload
		data = decoder.decode(f.read())

	#人物を追加する
	user_name = "{}_{}".format(data["last"],data["first"])
	r = CF.person.create(person_group_id, user_name)
	personId = r["personId"]
	os.mkdir("/home/pi/2018-KosenProcon/faceAPI_config/"+personId)
	shutil.copyfile("/home/pi/2018-KosenProcon/cache/upload/target_info.json", "/home/pi/2018-KosenProcon/faceAPI_config/"+personId+"/"+user_name+".json")
	add_personId(personId, data["last"], data["first"], data["last_kana"], data["first_kana"])

	return user_name, personId


def Add_Face(name, personId):
	decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict) #jsonファイルの辞書を順番通りにload
	with open("/home/pi/2018-KosenProcon/faceAPI_config/"+personId+"/"+name+".json") as f:
		data = decoder.decode(f.read())

	path = "/home/pi/2018-KosenProcon/cache/upload/"
	files = [relpath(x, path) for x in glob(join(path, '*.jpg'))]
	
	#人物の写真を追加する
	for i, file in enumerate(files):
		image = "/home/pi/2018-KosenProcon/cache/upload/{}".format(file)
		try:
			r = CF.person.add_face(image, person_group_id, personId)
			destination = "/home/pi/2018-KosenProcon/faceAPI_config/{}/{}.jpg".format(personId, r["persistedFaceId"])
			shutil.copyfile(image, destination)
			os.system("rm "+image)
			time.sleep(1)
		except Exception as e:
			pass


def train():
	r = CF.person_group.train(person_group_id)

def person_list():
	r = CF.person.lists(person_group_id)
	print("{}".format(json.dumps(r,indent=4)))

r = create()
Add_Face(r[0], r[1])
train()