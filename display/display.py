# smRecomend.artmirror.py
# requirements
# requests, feedparser, traceback, Pillow
# coding: UTF-8
# -*- coding: utf-8 -*-

from tkinter import *
import locale
import threading
import time
import requests
import json
import traceback
import feedparser
import lib.base as da
import copy
from PIL import Image, ImageTk
from contextlib import contextmanager
import random
import matplotlib.pyplot as plt
import lib.wlan0 as wl
ipaddress,host_name = wl.ip_check()

# 必要なフォルダの存在を確認する
import os
if not os.path.isdir("./graph/"):
	os.system("mkdir "+"./graph/")

import sys,os
sys.path.append("/home/pi/2018-KosenProcon/lib")
#データベースを使うためのライブラリ
from db import DB
db = DB()

import lib.cal

#グラフが非表示の際のグラフデータ作成
if not os.path.isfile("./graph/black.png"):
	#グラフ作成関数(y軸座標データ,ファイル名,グラフの色)
	da.graph([1,1,1,1,1,1],"black.png","black")

text_color = "#ffffff" #デフォルトの文字、その他の色
graph_size = (950,425) #グラフの大きさ
LOCALE_LOCK = threading.Lock()
ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = 24 # 時間表示設定
date_format = "%b %d, %Y" # check python doc for strftime() for options
redraw_time = 2000 #ms
#文字サイズ設定
BIG_text_size = 80
xlarge_text_size = 55
large_text_size = 45
medium_text_size = 35
small_text_size = 25
vsmall_text_size = 15

@contextmanager
def setlocale(name): #ロケーションの設定
	with LOCALE_LOCK:
		saved = locale.setlocale(locale.LC_ALL)
		try:
			yield locale.setlocale(locale.LC_ALL, name)
		finally:
			locale.setlocale(locale.LC_ALL, saved)

class Clock(Frame): #時間表示
	def __init__(self, parent, *args, **kwargs): #フレームの初期設定
		Frame.__init__(self, parent, bg='black')
		self.topFrm = Frame(self, bg="black")
		self.topFrm.pack(side=TOP, anchor=W)
		self.dateLbl = Label(self.topFrm, font=('Helvetica', xlarge_text_size,"bold"), bg="black")
		self.dateLbl.pack(side=LEFT, anchor=W)
		self.dayOWLbl = Label(self.topFrm, font=('Helvetica', large_text_size), bg="black")
		self.dayOWLbl.pack(side=RIGHT, anchor=E)
		self.timeLbl = Label(self, font=('Helvetica', BIG_text_size, "bold"), bg="black")
		self.timeLbl.pack(side=LEFT, anchor=N)
		self.tick()

	def tick(self): #表示内容の管理
		with setlocale(ui_locale):
			if time_format == 12:
				time2 = time.strftime('%I:%M %p') #12時間表示
			else:
				time2 = time.strftime('%H:%M') #24時間表示
			day_of_week2 = time.strftime('%A')
			date2 = time.strftime(date_format)
			date2_2 = date2.split(" ")
			date2_3 = date2_2[0][0:2]+"/"+date2_2[1][0:2]+" " #表示される情報の整理
			self.color = "#"+db.display_status_check("color") #表示する色のデータ取得
			if ((db.display_status_check("time") == "1") and (db.display_status_check("everything")=="1")): #表示 or 非表示の判定
				self.dayOWLbl.config(text=day_of_week2,fg=self.color)
				self.dateLbl.config(text=date2_3,fg=self.color)
				self.timeLbl.config(text=time2,fg=self.color)
			else: #表示を消す
				self.dayOWLbl.config(text="")
				self.dateLbl.config(text="")
				self.timeLbl.config(text="")
			self.timeLbl.after(redraw_time, self.tick) #再描画(redraW_time待機)

class Weather(Frame): #天気情報表示
	weather2,icon2,temperature2,currently2,forecast2= da.weather_setup() #天気情報の取得
	db.weather_update("ミヤコノジョウ",currently2,temperature2) #天気情報の更新
	def __init__(self, parent, *args, **kwargs): #初期設定
		Frame.__init__(self, parent, bg='black')
		self.old_colors = "#ffffff"
		self.start = time.time() 
		self.temperature = ''
		self.forecast = ''
		self.location = ''
		self.currently = ''
		self.icon = ''
		self.degreeFrm = Frame(self, bg="black")
		self.degreeFrm.pack(side=TOP, anchor=E)
		self.frame2 = Frame(self, bg="black")
		self.frame2.pack(side=TOP, anchor=E)
		self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', xlarge_text_size,"bold"), bg="black")
		self.temperatureLbl.pack(side=LEFT, anchor=N)
		self.iconLbl = Label(self.degreeFrm, bg="black")
		self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
		self.currentlyLbl = Label(self.frame2, font=('Helvetica', large_text_size), bg="black")
		self.currentlyLbl.pack(side=LEFT, anchor=W)
		self.forecastLbl = Label(self, font=('Helvetica', vsmall_text_size), bg="black")
		self.forecastLbl.pack(side=TOP, anchor=E)
		self.locationLbl = Label(self.frame2, font=('Helvetica', large_text_size), bg="black")
		self.locationLbl.pack(side=LEFT, anchor=E, padx=20)
		self.get_weather() #事前に天気を取得する
		self.display()

	def get_ip(self): #
		try:
			ip_url = "http://jsonip.com/"
			req = requests.get(ip_url)
			ip_json = json.loads(req.text)
			return ip_json['ip']
		except Exception as e:
			traceback.print_exc()
			return "Error: %s. Cannot get ip." % e


	def display(self):
		#データベースを確認して、ディスプレイに表示するか決める。
		if ((db.display_status_check("weather")=="1") and (db.display_status_check("everything")=="1")): #表示 or 非表示の判定
			text_colors = "#"+db.display_status_check("color") #表示する色のデータ取得
			self.elapsed_time = time.time() - self.start
			if self.elapsed_time>60*10: #APIの呼び出しを制限
				self.get_weather()
				print("call darkAPI")
				self.start = time.time() #時間をリセット
			if text_colors != self.old_colors:
				self.image_2 = da.image_change(self.image,text_colors)
				image_2 = self.image_2.resize((xlarge_text_size*2, xlarge_text_size*2), Image.ANTIALIAS)
				image_2 = image_2.convert('RGB')
				photo = ImageTk.PhotoImage(image_2)
				self.photo = photo
				self.old_colors = text_color
			self.currentlyLbl.config(text=self.currently, fg=text_colors)
			self.forecastLbl.config(text=self.forecast, fg=text_colors)
			self.temperatureLbl.config(text=self.temperature, fg=text_colors)
			self.locationLbl.config(text=self.location, fg=text_colors)
			self.iconLbl.config(image=self.photo)
		else: #表示を消す
			self.currentlyLbl.config(text="")
			self.forecastLbl.config(text="")
			self.temperatureLbl.config(text="")
			self.locationLbl.config(text="")
			self.iconLbl.config(image='')
		self.after(redraw_time, self.display)

	def get_weather(self):
		try:
			Weather.weather2,icon2,temperature2,currently2,forecast2= da.weather_setup()
			db.weather_update("ミヤコノジョウ",currently2,temperature2)
			if icon2 is not None:
				if self.icon != icon2:
					self.icon = icon2
					self.image = Image.open(icon2)
					image_2 = self.image.resize((xlarge_text_size*2, xlarge_text_size*2), Image.ANTIALIAS)
					image_2 = image_2.convert('RGB')
					photo = ImageTk.PhotoImage(image_2)
					self.photo = photo
			else:
				# remove image
				self.iconLbl.config(image='')

			location2 = "都城市"

			if self.currently != currently2:
				self.currently = currently2
			if self.forecast != forecast2:
				self.forecast = forecast2
			if self.temperature != temperature2:
				self.temperature = temperature2
			if self.location != location2:
				if location2 == ", ":
					self.location = "Cannot Pinpoint Location"
					self.locationLbl.config(text="Cannot Pinpoint Location", fg=text_color)
				else:
					self.location = location2
					self.locationLbl.config(text=location2, fg=text_color)
		except Exception as e:
			traceback.print_exc()
			print ("Error: %s. Cannot get weather." % e)

class Graph(Frame):
	kibun = 0
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		self.login_flag = 1
		self.old_personID = None
		self.old_color = "#ffffff"
		self.kibun = '～過去1週間のあなたの気分～'
		self.head = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
		self.head.pack(side=TOP, anchor=N)
		self.head.config(text=self.kibun)
		black_image = Image.open("./graph/black.png")
		black_image = black_image.resize(graph_size, Image.ANTIALIAS)
		logo_image = Image.open("./assets/kyo.png")
		logo_image = logo_image.resize((80,60), Image.ANTIALIAS)
		self.logo_photo = ImageTk.PhotoImage(logo_image)
		self.black_photo = ImageTk.PhotoImage(black_image)
		self.iconLbl = Label(self, bg='black')
		self.iconLbl.pack(side=TOP, anchor=N)
		self.logoFrame = Frame(self, bg="black")
		self.logoFrame.pack(side=BOTTOM, anchor=E)
		self.ip_logo = Label(self.logoFrame, fg="white", bg="black")
		self.ip_logo.pack(side=LEFT, anchor=W)
		self.ip_logo.config(image=self.logo_photo)
		self.ip_host = Label(self.logoFrame, font=('Helvetica', vsmall_text_size), fg="white", bg="black")
		self.ip_host.pack(side=RIGHT, anchor=W)
		self.ip_host.config(text=host_name+"\nhttp://"+ipaddress)
		self.display()

	def display(self):
		if ((db.display_status_check("history") == "1") and (db.display_status_check("everything")=="1") and (db.display_status_check("analysis_end")=="1")): #表示 or 非表示の判定
			text_color = "#"+db.display_status_check("color") #表示する色のデータ取得
			personID = db.currentUser_check()["personId"]
			#print(personID)
			if personID == "":
				self.photo = self.black_photo
				self.kibun = ""
			else:
				if ((personID != self.old_personID) or (self.login_flag == 0)):  
					Graph.kibun,datetime = da.emotion_data(personID)
					print(Graph.kibun)
					Recomend.art,Recomend.mus,Recomend.kibun_now,Recomend.place = da.rec_k(Graph.kibun[6],Weather.weather2)
					da.graph(datetime,Graph.kibun,"output.png","#ffffff")
					global image_n
					image_n = Image.open("./graph/output.png")
					self.image_re = image_n.resize(graph_size, Image.ANTIALIAS)
					self.photo = ImageTk.PhotoImage(self.image_re)
					self.login_flag = 1
					self.old_personID = personID
					self.old_color = "#ffffff"
			if text_color != self.old_color:
				image_c = da.image_change(image_n,text_color)
				self.old_color = text_color
				self.image_re = image_c.resize(graph_size, Image.ANTIALIAS)
				self.photo = ImageTk.PhotoImage(self.image_re)

			self.head.config(text=self.kibun, fg=text_color)
			self.iconLbl.config(image=self.photo)
		else: #表示を消す
			self.head.config(text="")
			self.iconLbl.config(image=self.black_photo)
			self.login_flag = 0

		self.after(redraw_time, self.display)
class Recomend(Frame):
	art,mus,kibun_now,place = da.rec_k(Graph.kibun,Weather.weather2)
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		Frame.__init__(self, parent, bg='black')
		self.date1 = '今のあなたの気分は...'
		self.bun1 = Label(self, font=('Helvetica', small_text_size), fg=text_color, bg="black")
		self.bun1.pack(side=BOTTOM, anchor=E)
		self.date2 = '"'+Recomend.kibun_now+'" みたいなので'
		self.bun2 = Label(self, font=('Helvetica', small_text_size), fg=text_color, bg="black")
		self.bun2.pack(side=BOTTOM, anchor=N)
		self.date3 = '"'+Recomend.art+'"の"'+Recomend.mus+'"を聴きながら'+Recomend.place
		self.bun3 = Label(self, font=('Helvetica', small_text_size), fg=text_color, bg="black")
		self.bun3.pack(side=BOTTOM, anchor=N)
		self.date4 = '過ごしてはいかがでしょうか？'
		self.bun4 = Label(self, font=('Helvetica', small_text_size), fg=text_color, bg="black")
		self.bun4.pack(side=BOTTOM, anchor=W)
		self.display()

	def display(self):
		if ((db.display_status_check("recommendation") == "1") and (db.display_status_check("everything")=="1") and (db.display_status_check("analysis_end")=="1")): #表示 or 非表示の判定
			text_color = "#"+db.display_status_check("color") #表示する色のデータ取得
			self.date3 = '"'+Recomend.art+'"の"'+Recomend.mus+'"を聴きながら'+Recomend.place
			self.date2 = '"'+Recomend.kibun_now+'" みたいなので'
			self.bun1.config(text=self.date4, fg=text_color)
			self.bun2.config(text=self.date3, fg=text_color)
			self.bun3.config(text=self.date2, fg=text_color)
			self.bun4.config(text=self.date1, fg=text_color)
		else: #表示を消す
			self.bun4.config(text="")
			self.bun3.config(text="")
			self.bun2.config(text="")
			self.bun1.config(text="")

		self.after(redraw_time, self.display)

class CalendarEvent(Frame):
	def __init__(self, parent, event_name="Event 1"):
		Frame.__init__(self, parent, bg='black')
		#初期設定
		self.login_flag = 0
		self.old_calenderID = None
		#タイトル
		self.title = '   ～今日の予定～'
		self.head = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.head.pack(side=TOP, anchor=N)
		self.head.config(text=self.title)		
		#予定 
		self.eventNameLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
		self.eventNameLbl.pack(side=TOP, anchor=N)
		
		self.organize_event()

	def organize_event(self):
		#データベースを確認して、ディスプレイに表示するか決める。
		if ((db.display_status_check("calendar")=="1") and (db.display_status_check("authentication")=="1") and (db.display_status_check("everything")=="1")): #表示 or 非表示の判定
			text_color = "#"+db.display_status_check("color") #表示する色のデータ取得
			personID = db.currentUser_check()["personId"]
			calenderID = db.personId_to_calendarId(personID)['calendarId']  #calenderIDを取得する関数
			if (calenderID == None):
				self.eventNameLbl.config(text="")
				self.head.config(text="")
			else:
				if ((calenderID != self.old_calenderID) or (self.login_flag == 0)): 
					self.get_event(calenderID)
					self.old_calenderID = calenderID
					self.login_flag = 1
					print("calendar update")
				self.eventNameLbl.config(text=self.cal, fg=text_color)
				self.head.config(text=self.title, fg=text_color)
		else: #表示を消す
			self.eventNameLbl.config(text="")
			self.head.config(text="")
			self.login_flag = 0

		self.eventNameLbl.after(redraw_time, self.organize_event) #指定mSで画面を更新する

	def get_event(self,calenderID):# googlecalendarからイベントを取得し、整形する
		events = lib.cal.main(calenderID)
		if len(events)>0:
			self.cal=""
			for event in events:
				self.cal =self.cal + "{}:{}～{}\n".format(event[0],event[1],event[2])
		else:
			self.cal="今日の予定はありません"


class FullscreenWindow:

	def __init__(self):
		self.tk = Tk()
		self.tk.configure(background='black')
		self.topFrame = Frame(self.tk, background = 'black')
		self.subtopFrame = Frame(self.tk, background = 'black')
		self.bottomFrame = Frame(self.tk, background = 'black')
		self.botFrame = Frame(self.tk, background = 'black')
		self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
		self.subtopFrame.pack(side = TOP, fill=BOTH, expand = YES)
		self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
		self.botFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
		self.state = False
		self.toggle_fullscreen()
		self.tk.bind("<Return>", self.toggle_fullscreen)
		self.tk.bind("<Escape>", self.end_fullscreen)

		self.clock = Clock(self.topFrame)
		self.clock.pack(side=LEFT, anchor=N, padx=10, pady=10)
	
		self.weather = Weather(self.topFrame)
		self.weather.pack(side=RIGHT, anchor=N, padx=10, pady=10)
	
		self.gra = Graph(self.bottomFrame)
		self.gra.pack(side = BOTTOM, anchor=CENTER, padx=10, pady=0)

		self.rec = Recomend(self.botFrame)
		self.rec.pack(side=TOP, anchor=CENTER, padx=10, pady=0)

		self.gra = CalendarEvent(self.subtopFrame)
		self.gra.pack(side = TOP, anchor=N, padx=10, pady=0)

	def toggle_fullscreen(self, event=None):
		self.state = not self.state  # Just toggling the boolean
		self.tk.attributes("-fullscreen", self.state)
		return "break"

	def end_fullscreen(self, event=None):
		self.state = False
		self.tk.attributes("-fullscreen", False)
		return "break"

if __name__ == '__main__':
	w = FullscreenWindow()
	w.tk.mainloop()