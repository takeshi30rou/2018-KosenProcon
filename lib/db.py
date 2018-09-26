# -*- coding: utf-8 -*-
import pymysql.cursors

class DB:
	def connection(self): # MySQLに接続する
		self.c = pymysql.connect(host='localhost',
		                             user='pi',
		                             password='raspberry',
		                             db='katori',
		                             charset='utf8',
		                             # cursorclassを指定することで
		                             # Select結果をtupleではなくdictionaryで受け取れる
		                             cursorclass=pymysql.cursors.DictCursor)

	def get_name(self, personId):
		# MySQLに接続する
		self.connection()
		try:
			# Insert処理
			with self.c.cursor() as cursor:
				sql = "SELECT * FROM personIds WHERE personId = %s"
				#print(sql)
				cursor.execute(sql, (personId))
				result = cursor.fetchone()
				#print(result)
				return result

		finally:
			# MySQLから切断する
			self.c.close()

	def emotion_1(self, detect_result, personId):
		# MySQLに接続する
		self.connection()

		emotion = []
		emotion.append(detect_result[0]["faceAttributes"]["emotion"]["anger"])
		emotion.append(detect_result[0]["faceAttributes"]["emotion"]["contempt"])
		emotion.append(detect_result[0]["faceAttributes"]["emotion"]["disgust"])
		emotion.append(detect_result[0]["faceAttributes"]["emotion"]["fear"])
		emotion.append(detect_result[0]["faceAttributes"]["emotion"]["happiness"])
		emotion.append(detect_result[0]["faceAttributes"]["emotion"]["neutral"])
		emotion.append(detect_result[0]["faceAttributes"]["emotion"]["sadness"])
		emotion.append(detect_result[0]["faceAttributes"]["emotion"]["surprise"])

		try:
			# Insert処理
			with self.c.cursor() as cursor:
			    sql = "INSERT INTO emotion"\
			    " (personId, anger, contempt, disgust, fear, happiness, neutral, sadness, surprise) "\
			    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
			    #print(sql)
			    r = cursor.execute(sql, (personId, *emotion))
			    #print(r) # -> 1
			    # autocommitではないので、明示的にコミットする
			    self.c.commit()
		finally:
			# MySQLから切断する
			self.c.close()

	def emotion_2(self, emotion_result, personId):
		# MySQLに接続する
		self.connection()

		label = {0:'angry',1:'disgust',2:'fear',3:'happy',4:'sad',5:'surprise',6:'neutral'}

		emotion = []
		for i in range(7):
			emotion.append(emotion_result[label[i]])

		try:
			# Insert処理
			with self.c.cursor() as cursor:
			    sql = "INSERT INTO emotion2"\
			    " (personId,angry,disgust,fear,happy,sad,surprise,neutral) "\
			    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			    #print(sql)
			    r = cursor.execute(sql, (personId, *emotion))
			    #print(r) # -> 1
			    # autocommitではないので、明示的にコミットする
			    self.c.commit()
		finally:
			# MySQLから切断する
			self.c.close()

	def display_status_check(self,service):
		# MySQLに接続する
		self.connection()

		try:
			# select処理
			with self.c.cursor() as cursor:
				sql = "SELECT `switch` FROM `display` WHERE `service`=%s"
				#print(sql)
				cursor.execute(sql, service)
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
				# Select結果を取り出す
				result = cursor.fetchone()
				return result["switch"]
		finally:
			# MySQLから切断する
			self.c.close()

	def display_status_update(self,service,status):
		# MySQLに接続する
		self.connection()
		try:
			# select処理
			with self.c.cursor() as cursor:
				sql = "UPDATE `display` SET `switch`=%s WHERE `service`=%s"
				#print(sql)
				cursor.execute(sql, (status, service))
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
		finally:
			# MySQLから切断する
			self.c.close()

if __name__ == '__main__':
	db = DB()
	db.display_status_update("authentication",0)
	db.display_status_update("authentication",0)