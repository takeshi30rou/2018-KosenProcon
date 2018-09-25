# smartmirror.py
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

from PIL import Image, ImageTk
from contextlib import contextmanager

import random
import matplotlib.pyplot as plt

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

line_b = 0
def graph(y):
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.patch.set_facecolor('none')
	ax.spines["right"].set_color("none")
	ax.spines["top"].set_color("none")
	ax.spines["left"].set_color("white")
	ax.spines["bottom"].set_color("white")
	ax.tick_params(axis = 'x', colors ='white')
	ax.tick_params(axis = 'y', colors = 'white')
	ax.plot(y,color="white")
	filename = "./graph/output.png"
	plt.savefig(filename,facecolor="none",edgecolor="none")

import time

LOCALE_LOCK = threading.Lock()

ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = 24 # 12 or 24
date_format = "%b %d, %Y" # check python doc for strftime() for options
news_country_code = 'us'
xlarge_text_size = 40
large_text_size = 25
medium_text_size = 18
small_text_size = 12

@contextmanager
def setlocale(name): #thread proof function to work with locale
	with LOCALE_LOCK:
		saved = locale.setlocale(locale.LC_ALL)
		try:
			yield locale.setlocale(locale.LC_ALL, name)
		finally:
			locale.setlocale(locale.LC_ALL, saved)

class Clock(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		self.date1 = ''
		self.dateLbl = Label(self, text=self.date1, font=('Helvetica', large_text_size), fg="white", bg="black")
		self.dateLbl.pack(side=TOP, anchor=W)
		self.day_of_week1 = ''
		self.dayOWLbl = Label(self, text=self.day_of_week1, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.dayOWLbl.pack(side=TOP, anchor=W)
		self.time1 = ''
		self.timeLbl = Label(self, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
		self.timeLbl.pack(side=TOP, anchor=W)
		self.tick()

	def tick(self):
		with setlocale(ui_locale):
			if time_format == 12:
				time2 = time.strftime('%I:%M %p') #hour in 12h format
			else:
				time2 = time.strftime('%H:%M') #hour in 24h format

			day_of_week2 = time.strftime('%A')
			date2 = time.strftime(date_format)

			if db.display_status_check("time"):
				# if time string has changed, update it
				if day_of_week2 != self.day_of_week1:
					self.day_of_week1 = day_of_week2
					self.dayOWLbl.config(text=day_of_week2)
				if date2 != self.date1:
					self.date1 = date2
					date2_2 = date2.split(" ")
					date2_3 = date2_2[3]+"/"+date2_2[1][0:1]+"/"+date2_2[2][0:2]
					#print(date2_3)
					self.dateLbl.config(text=date2_3)
				if time2 != self.time1:
					self.time1 = time2
					self.timeLbl.config(text=time2)
			else:
				self.day_of_week1 = ""
				self.date1 = ""
				self.time1 = ""
				self.dayOWLbl.config(text="")
				self.dateLbl.config(text="")
				self.timeLbl.config(text="")
			self.timeLbl.after(200, self.tick)

class Weather(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		self.temperature = ''
		self.forecast = ''
		self.location = ''
		self.currently = ''
		self.icon = ''
		self.degreeFrm = Frame(self, bg="black")
		self.degreeFrm.pack(side=TOP, anchor=E)
		self.frame2 = Frame(self, bg="black")
		self.frame2.pack(side=TOP, anchor=E)
		self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
		self.temperatureLbl.pack(side=LEFT, anchor=N)
		self.iconLbl = Label(self.degreeFrm, bg="black")
		self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
		self.currentlyLbl = Label(self.frame2, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.currentlyLbl.pack(side=LEFT, anchor=W)
		self.forecastLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
		self.forecastLbl.pack(side=TOP, anchor=E)
		self.locationLbl = Label(self.frame2, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.locationLbl.pack(side=LEFT, anchor=E, padx=20)
		self.get_weather()

	def get_ip(self):
		try:
			ip_url = "http://jsonip.com/"
			req = requests.get(ip_url)
			ip_json = json.loads(req.text)
			return ip_json['ip']
		except Exception as e:
			traceback.print_exc()
			return "Error: %s. Cannot get ip." % e

	def get_weather(self):
		try:
			a,icon2,temperature2,currently2,forecast2= da.weather_setup()
			if icon2 is not None:
				if self.icon != icon2:
					self.icon = icon2
					image = Image.open(icon2)
					image = image.resize((70, 70), Image.ANTIALIAS)
					image = image.convert('RGB')
					photo = ImageTk.PhotoImage(image)

					self.iconLbl.config(image=photo)
					self.iconLbl.image = photo
			else:
				# remove image
				self.iconLbl.config(image='')

			location2 = "都城市"

			if self.currently != currently2:
				self.currently = currently2
				self.currentlyLbl.config(text=currently2)
			if self.forecast != forecast2:
				self.forecast = forecast2
				self.forecastLbl.config(text=forecast2)
			if self.temperature != temperature2:
				self.temperature = temperature2
				self.temperatureLbl.config(text=temperature2)
			if self.location != location2:
				if location2 == ", ":
					self.location = "Cannot Pinpoint Location"
					self.locationLbl.config(text="Cannot Pinpoint Location")
				else:
					self.location = location2
					self.locationLbl.config(text=location2)
		except Exception as e:
			traceback.print_exc()
			print ("Error: %s. Cannot get weather." % e)

		self.after(60000, self.get_weather)

class Recomend(Frame):
	def __init__(self, parent,art,mus,kibun_now,place, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		self.date1 = '今のあなたの気分は...'
		self.bun1 = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.bun1.pack(side=TOP, anchor=W)
		self.date2 = '"'+kibun_now+'" みたいなので'
		self.bun2 = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.bun2.pack(side=TOP, anchor=S)
		self.date3 = '"'+art+'"の"'+mus+'"'
		self.bun3 = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.bun3.pack(side=TOP, anchor=W)
		self.date4 = 'を聴きながら'+place
		self.bun4 = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.bun4.pack(side=TOP, anchor=W)
		self.date5 = 'で過ごしてはいかがでしょうか？'
		self.bun5 = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.bun5.pack(side=TOP, anchor=W)
		self.bun1.config(text=self.date1)
		self.bun2.config(text=self.date2)
		self.bun3.config(text=self.date3)
		self.bun4.config(text=self.date4)
		self.bun5.config(text=self.date5)

class Graph(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		self.kibun = '～過去1週間のあなたの気分～'
		self.head = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.head.pack(side=TOP, anchor=N)
		self.head.config(text=self.kibun)
		image = Image.open("./graph/output.png")
		image = image.resize((400, 300), Image.ANTIALIAS)
		#image = image.convert('RGB')
		photo = ImageTk.PhotoImage(image)
		self.iconLbl = Label(self, bg='black', image=photo)
		self.iconLbl.image = photo
		self.iconLbl.pack(side=TOP, anchor=N)

class CalendarEvent(Frame):
	def __init__(self, parent, event_name="Event 1"):
		Frame.__init__(self, parent, bg='black')
		#初期設定
		self.start = time.time()
		#タイトル
		self.title = '～今日の予定～'
		self.head = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
		self.head.pack(side=TOP, anchor=CENTER)
		self.head.config(text=self.title)		
		#予定 
		self.get_event()
		self.eventNameLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
		self.eventNameLbl.pack(side=TOP, anchor=W)
		
		self.organize_event()

	def organize_event(self):
		#データベースを確認して、ディスプレイに表示するか決める。
		if db.display_status_check("calendar") and db.display_status_check("authentication"):
			self.title = '～今日の予定～'
			self.elapsed_time = time.time() - self.start
			if self.elapsed_time>60*60: #APIの呼び出しを制限（指定秒ごとにカレンダーを取得）
				self.get_event()
				print("calendar update")
				self.start = time.time()
		else: #表示を消す
			self.cal=""
			self.title=""
		#画面更新
		self.eventNameLbl.config(text=self.cal)
		self.head.config(text=self.title)
		self.eventNameLbl.after(200, self.organize_event) #指定mSで画面を更新する

	def get_event(self):# googlecalendarからイベントを取得し、整形する
		events = lib.cal.main()
		if len(events)>0:
			self.cal=""
			for event in events:
				self.cal =self.cal + "{}:{}～{}\n".format(event[0],event[1],event[2])
		else:
			self.cal="今日の予定はありません"


class FullscreenWindow:

	def __init__(self,clock_num,kibunnn,art,mus,kibun_now,place):
		self.tk = Tk()
		self.tk.configure(background='black')
		self.topFrame = Frame(self.tk, background = 'black')
		self.bottomFrame = Frame(self.tk, background = 'black')
		self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
		self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
		self.state = False
		self.toggle_fullscreen()
		self.tk.bind("<Return>", self.toggle_fullscreen)
		self.tk.bind("<Escape>", self.end_fullscreen)
		# clock
		if clock_num == 1 :
			self.clock = Clock(self.topFrame)
			self.clock.pack(side=LEFT, anchor=N, padx=10, pady=10)
		if weather_num == 1 :
			self.weather = Weather(self.topFrame)
			self.weather.pack(side=RIGHT, anchor=N, padx=10, pady=10)
		if recomend_num == 1 :
			self.rec = Recomend(self.bottomFrame,art,mus,kibun_now,place)
			self.rec.pack(side=LEFT, anchor=W, padx=10, pady=line_b)
		if graph_num == 1 :
			self.gra = Graph(self.bottomFrame)
			self.gra.pack(side = RIGHT, anchor=E, padx=10, pady=line_b)
		self.gra = CalendarEvent(self.bottomFrame)
		self.gra.pack(side = RIGHT, anchor=E, padx=10, pady=line_b)

	def toggle_fullscreen(self, event=None):
		self.state = not self.state  # Just toggling the boolean
		self.tk.attributes("-fullscreen", self.state)
		return "break"

	def end_fullscreen(self, event=None):
		self.state = False
		self.tk.attributes("-fullscreen", False)
		return "break"

if __name__ == '__main__':
	list_y = []
	for i in range(7):
		j = random.randrange(10)
		list_y.append(j)
	kibunnn = list_y[6]
	clock_num = 1
	weather_num = clock_num
	recomend_num = 1
	graph_num = 1
	a,b,c,d,e = da.weather_setup()
	art,mus,kibun_now,place = da.rec_k(kibunnn,a)
	graph(list_y)
	w = FullscreenWindow(clock_num,kibunnn,art,mus,kibun_now,place)
	w.tk.mainloop()