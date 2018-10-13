import requests
import json
import matplotlib.pyplot as plt
import sys,os
sys.path.append("/home/pi/2018-KosenProcon/")
from apikey import *
#from __future__ import unicode_literals, print_function, absolute_import
from PIL import Image, ImageChops
import copy
import sys,os
sys.path.append("/home/pi/2018-KosenProcon/lib")
#データベースを使うためのライブラリ
from db import DB
db = DB()

weather_api_token = darksky_APIKEY # create account at https://darksky.net/dev/
weather_lang = 'ja' # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'us' # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = "31.766109" # Set this if IP location lookup does not work for you (must be a string)
longitude = "131.091977" # Set this if IP location lookup does not work for you (must be a string)

icon_lookup = {
    'clear-day': "./assets/Sun.png",  # clear sky day
    'wind': "./assets/Wind.png",   #wind
    'cloudy': "./assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "./assets/PartlySunny.png",  # partly cloudy day
    'rain': "./assets/Rain.png",  # rain day
    'snow': "./assets/Snow.png",  # snow day
    'snow-thin': "./assets/Snow.png",  # sleet day
    'fog': "./assets/Haze.png",  # fog day
    'clear-night': "./assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "./assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "./assets/Storm.png",  # thunderstorm
    'tornado': "./assests/Tornado.png",    # tornado
    'hail': "./assests/Hail.png"  # hail
}
icon_lookup_2 = {
    'clear-day': 0,
    'wind': 1,
    'cloudy': 2,
    'partly-cloudy-day': 3,
    'rain': 4,
    'snow': 5,
    'snow-thin': 6,
    'fog': 7,
    'clear-night': 8,
    'partly-cloudy-night': 9,
    'thunderstorm': 10,
    'tornado': 11,
    'hail': 12
}

def rec_k(kib,wet):
    if ((kib >= 0) and (kib <3)):
        kibun_now = "元気がない"
        if ((wet == 0) or (wet == 8)):
            Artist = "YUI"
            Music = "Driving Happy Life"
            bs = "ドライブをして"
        if ((wet == 5) or (wet == 6)):
            Artist = "YUI"
            Music = "Muffler"
            bs = "家でゆっくり"
        if ((wet == 4) or (wet == 7)):
            Artist = "YUI"
            Music = "Rain"
            bs = "家でゆっくり"
        if ((wet == 1) or (wet == 2) or (wet == 3) or (wet == 9)):
            Artist = "YUI"
            Music = "Cloudy"
            bs = "家でゆっくり"
        if ((wet == 10) or (wet == 11) or (wet == 12)):
            Artist = "YUI"
            Music = "Rolling star"
            bs = "家でゆっくり"
    if ((kib >= 3) and (kib <7)):
        kibun_now = "何とも言えない"
        if ((wet == 0) or (wet == 8)):
            Artist = "BUMP OF CHICKEN"
            Music = "ray"
            bs = "ドライブをして"
        if ((wet == 5) or (wet == 6)):
            Artist = "BUMP OF CHICKEN"
            Music = "スノースマイル"
            bs = "家でゆっくり"
        if ((wet == 4) or (wet == 7)):
            Artist = "BUMP OF CHICKEN"
            Music = "虹を待つ人"
            bs = "家でゆっくり"
        if ((wet == 1) or (wet == 2) or (wet == 3) or (wet == 9)):
            Artist = "米津玄師"
            Music = "Lemon"
            bs = "家でゆっくり"
        if ((wet == 10) or (wet == 11) or (wet == 12)):
            Artist = "BUMP OF CHICKEN"
            Music = "メーデー"
            bs = "家でゆっくり"
    if (kib >= 7):
        kibun_now = "元気いっぱい"
        if ((wet == 0) or (wet == 8)):
            Artist = "RADWIMPS"
            Music = "君と羊と青"
            bs = "ドライブをして"
        if ((wet == 5) or (wet == 6)):
            Artist = "米津玄師"
            Music = "orion"
            bs = "家でゆっくり"
        if ((wet == 4) or (wet == 7)):
            Artist = "RADWIMPS"
            Music = "カタルシスト"
            bs = "家でゆっくり"
        if ((wet == 1) or (wet == 2) or (wet == 3) or (wet == 9)):
            Artist = "米津玄師"
            Music = "アイネクライネ"
            bs = "家でゆっくり"
        if ((wet == 10) or (wet == 11) or (wet == 12)):
            Artist = "日本"
            Music = "国歌"
            bs = "家でゆっくり"
    return Artist,Music,kibun_now,bs
def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

def weather_setup():
    if latitude is None and longitude is None:
        # get location
        location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
        r = requests.get(location_req_url)
        location_obj = json.loads(r.text)

        lat = location_obj['latitude']
        lon = location_obj['longitude']

        location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

        # get weather
        weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, lat,lon,weather_lang,weather_unit)
    else:
        location2 = ""
        # get weather
        weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, latitude, longitude, weather_lang, weather_unit)

    r = requests.get(weather_req_url)
    weather_obj = json.loads(r.text)

    degree_sign= '℃'
    temperature2 = "%s%s" % (str(round(((int(weather_obj['currently']['temperature'])-32)/1.8),1)), degree_sign)
    currently2 = weather_obj['currently']['summary']
    forecast2 = weather_obj["hourly"]["summary"]

    icon_id = weather_obj['currently']['icon']
    icon2 = None
    weather_num = 1

    if icon_id in icon_lookup:
        icon2 = icon_lookup[icon_id]
        weather_num = icon_lookup_2[icon_id]
    return weather_num,icon2,temperature2,currently2,forecast2

def graph(data_x,data_y,file_name,color):
    plt.rcParams["font.size"] = 18
    fig = plt.figure(figsize=(10,4.5),dpi=200)
    ax = fig.add_subplot(111)
    ax.patch.set_facecolor('none')
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")
    ax.spines["left"].set_color(color)
    ax.spines["bottom"].set_color(color)
    ax.tick_params(axis = 'x', colors =color)
    ax.tick_params(axis = 'y', colors = color)
    ax.plot(data_y,color=color)
    data_x.reverse()
    data_x.append("")
    data_x.reverse()
    ax.set_xticklabels(data_x, rotation=10, fontsize='small',color=color)
    filename = "./graph/"+file_name
    plt.savefig(filename,facecolor="black",edgecolor="white")

def image_change(img_n,color):
    img = copy.deepcopy(img_n)
    r, g, b, a = img.split()
    src_color = (255, 255, 255)
    _r = r.point(lambda _: 1 if _ == src_color[0] else 0, mode="1")
    _g = g.point(lambda _: 1 if _ == src_color[1] else 0, mode="1")
    _b = b.point(lambda _: 1 if _ == src_color[2] else 0, mode="1")
    mask = ImageChops.logical_and(_r, _g)
    mask = ImageChops.logical_and(mask, _b)
    dst_color = (int(color[1:3],16),int(color[3:5],16),int(color[5:7],16))
    img.paste(Image.new("RGB", img.size, dst_color), mask=mask)
    return img

def emotion_data(personID):
    kibunnn = db.emotion_status_check(personID)
    datetime = db.emotion_datetime_status_check(personID)
    kibun=[]
    dt = []
    num_k = len(kibunnn)
    num_d = len(datetime)
    if num_k < 7:
        for j in range(7 - num_k):
            kibunnn.append({"angry":0})
    if num_d < 7:
        for j in range(7 - num_d):
            datetime.append({"datetime":"-"})
    for i in range(7):
        kibun.append(kibunnn[i]["angry"])
        if datetime[i]["datetime"] != "-":
            datetime_1 = str(datetime[i]["datetime"]).split()[0][5:10] +" "+ str(datetime[i]["datetime"]).split()[1][0:5]
            dt.append(datetime_1)
        else:
            dt.append(datetime[i]["datetime"])
    dt.reverse()
    kibun.reverse()
    return kibun,dt