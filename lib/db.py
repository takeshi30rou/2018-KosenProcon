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

	def emotion(self, emotion_result, personId):
		latest = self.latest_emotion_index(personId)
		index = self.evaluation(emotion_result["happy"],emotion_result["sad"],emotion_result["neutral"])+latest["emotion_index"]
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
			    " (personId,angry,disgust,fear,happy,sad,surprise,neutral,emotion_index) "\
			    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
			    #print(sql)
			    r = cursor.execute(sql, (personId, *emotion, index))
			    #print(r) # -> 1
			    # autocommitではないので、明示的にコミットする
			    self.c.commit()
		finally:
			# MySQLから切断する
			self.c.close()

	def emotion3(self, emotion_result, personId, HR):
		# MySQLに接続する
		self.connection()

		label = {0:'angry',1:'disgust',2:'fear',3:'happy',4:'sad',5:'surprise',6:'neutral'}
		
		emotion = []
		for i in range(7):
			emotion.append(emotion_result[label[i]])

		try:
			# Insert処理
			with self.c.cursor() as cursor:
			    sql = "INSERT INTO emotion3"\
			    " (personId,angry,disgust,fear,happy,sad,surprise,neutral,HR) "\
			    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
			    #print(sql)
			    r = cursor.execute(sql, (personId, *emotion, HR))
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

	def emotion_status_check(self,userID):
		# MySQLに接続する
		self.connection()

		try:
			# select処理
			with self.c.cursor() as cursor:
				sql = "SELECT `emotion_index` FROM `emotion2` WHERE `personId`=%s ORDER BY `datetime` DESC"
				#print(sql)
				cursor.execute(sql,userID)
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
				# Select結果を取り出す
				result = cursor.fetchall()
				return result
		finally:
			# MySQLから切断する
			self.c.close()

	def emotion_datetime_status_check(self,userID):
		# MySQLに接続する
		self.connection()

		try:
			# select処理
			with self.c.cursor() as cursor:
				sql = "SELECT `datetime` FROM `emotion2` WHERE `personId`=%s ORDER BY `datetime` DESC"
				#print(sql)
				cursor.execute(sql,userID)
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
				# Select結果を取り出す
				result = cursor.fetchall()
				return result
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

	def currentUser_check(self):
		# MySQLに接続する
		self.connection()

		try:
			# select処理
			with self.c.cursor() as cursor:
				sql = "SELECT `personId` FROM `currentUser` WHERE 1"
				#print(sql)
				cursor.execute(sql)
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
				# Select結果を取り出す
				result = cursor.fetchone()
				return result
		finally:
			# MySQLから切断する
			self.c.close()

	def currentUser_update(self,personId):
		# MySQLに接続する
		self.connection()
		try:
			# select処理
			with self.c.cursor() as cursor:
				sql = "UPDATE `currentUser` SET `personId`=%s WHERE 1"
				#print(sql)
				cursor.execute(sql, personId)
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
		finally:
			# MySQLから切断する
			self.c.close()

	def weather_check(self):
		# MySQLに接続する
		self.connection()
		try:
			# select処理
			with self.c.cursor() as cursor:
				sql = "SELECT `place`, `weather`, `temperature` FROM `weather` WHERE 1"
				#print(sql)
				cursor.execute(sql)
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
				# Select結果を取り出す
				result = cursor.fetchone()
				return result
		finally:
			# MySQLから切断する
			self.c.close()

	def weather_update(self,place,weather,temperature):
		# MySQLに接続する
		self.connection()
		try:
			# select処理
			with self.c.cursor() as cursor:
				sql = "UPDATE `weather` SET `place`=%s,`weather`=%s,`temperature`=%s WHERE 1"
				#print(sql)
				cursor.execute(sql, (place, weather, temperature))
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
		finally:
			# MySQLから切断する
			self.c.close()

	def personId_to_calendarId(self,personId):
			# MySQLに接続する
		self.connection()
		try:
			# select処理
			with self.c.cursor() as cursor:
				sql = "SELECT `calendarId` FROM `calendarIds` WHERE `personId`= %s"
				#print(sql)
				cursor.execute(sql,personId)
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
				# Select結果を取り出す
				result = cursor.fetchone()
				return result
		finally:
			# MySQLから切断する
			self.c.close()

	def evaluation(self,happy,sad,neutral):
		y=0.000980305511429404+0.0222859331905098*happy-0.0225111298759341*sad+0.0000242095263100815*neutral
		return y

	def latest_emotion_index(self, personId):
		# MySQLに接続する
		self.connection()

		try:
			# Insert処理
			with self.c.cursor() as cursor:
				sql = "SELECT  `datetime`,`emotion_index` FROM `emotion2` WHERE `personId`=%s ORDER BY `datetime` DESC"
				print(sql)
				cursor.execute(sql,personId)
				# オートコミットじゃないので、明示的にコミットを書く必要がある
				self.c.commit()
				# Select結果を取り出す
				result = cursor.fetchone()
				if result == None:
					result = {"datetime":"-","emotion_index":0}
				return result
		except Exception as e:
				return {datetime:"-",emotion_index:0}
				print(e)
		finally:
			# MySQLから切断する
			self.c.close()
	
if __name__ == '__main__':
	db = DB()
	# db.display_status_update("authentication",0)
	# db.display_status_update("authentication",0)
	# db.currentUser_update("")
	# r = db.currentUser_check()
	# print(r["personId"])
	# r = db.display_status_check("time")
	ID = "8fdbf138-3a97-422b-ae5c-1f0093211bd7"
	r = {
    "neutral": 2.0068106651306152,
    "fear": 0.35729971528053284,
    "happy": 0.2814096212387085,
    "sad": 4.895124435424805,
    "disgust": 0.004688642453402281,
    "angry": 5.445241928100586,
    "surprise": 0.00942625105381012
}
	db.emotion(r, ID)
