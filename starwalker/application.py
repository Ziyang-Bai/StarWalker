# -*- coding: utf-8 -*- 
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
import requests
import pandas
import json
import urllib.parse
import hashlib
import urllib
def newMoonJudge(year, month, day, hour, minute):
    ts = load.timescale()
    t = ts.utc(year, month, day, hour, minute)

    eph = load('de421.bsp')
    sun, moon, earth = eph['sun'], eph['moon'], eph['earth']

    e = earth.at(t)
    _, slon, _ = e.observe(sun).apparent().frame_latlon(ecliptic_frame)
    _, mlon, _ = e.observe(moon).apparent().frame_latlon(ecliptic_frame)
    phase = (mlon.degrees - slon.degrees) % 360.0

    print('{0:.1f}'.format(phase))
    if '{0:.1f}'.format(phase) ==0:
        return True
    else:
        return False

def geodata():
    url = "http://api.geodatasource.com/city"
    params = { 'key': 'YKWZWPVPQNAOJHWQSNXQ5IBGPSKXETXD', 'format': 'json', 'lat': 37.3861, 'lng': -122.084 }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        print(response.text)
        rep = response.text
        data = json.loads(rep)
        city = data.get('city')
        print(city)
        return city
    else:
        print("请求失败，状态码：", response.status_code)
        return None

def direction_fullname(direction_abbr):
    direction_dict = {
        'N': '正北风',
        'S': '正南风',
        'E': '正东风',
        'W': '正西风',
        'NE': '东北风',
        'NW': '西北风',
        'SE': '东南风',
        'SW': '西南风'
    }
    return direction_dict.get(direction_abbr, '未知风向')

def precipitation_type_translate(prec_type):
    prec_type_dict = {
        'none': '无',
        'drizzle': '毛毛雨',
        'rain': '雨',
        'snow': '雪',
        'storm': '风暴',
        'thunder': '雷暴',
        'hail': '冰雹'
    }
    return prec_type_dict.get(prec_type.lower(), '未知降水类型')

def seventimer(lon, lat):
    url = "https://www.7timer.info/bin/astro.php"
    params = {"lon": lon, "lat": lat, "ac": "0", "unit": "metric", "output": "json", "tzshift": "0"}
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    else:
        print("请求失败，状态码：", response.status_code)
        return None

def print_data_in_2x5_format(data):
    if data:
        for i, item in enumerate(data["dataseries"]):
            if i % 5 == 0:
                print()
            print("时间点：",       f"{item['timepoint']:<3}", end="  ")
            print("云层覆盖：",    f"{item['cloudcover']:<3}", end="  ")
            print("视宁度：",      f"{item['seeing']:<3}", end="  ")
            print("透明度：",      f"{item['transparency']:<3}", end="  ")
            print("提升指数：",    f"{item['lifted_index']:<3}", end="  ")
            print("相对湿度：",    f"{item['rh2m']:<3}", end="  ")
            print("风速：",        f"{item['wind10m']['speed']:<3}", end="  ")
            print("风向：",        f"{direction_fullname(item['wind10m']['direction']):<3}", end="  ")
            print("温度：",        f"{item['temp2m']:<3}", end="  ")
            print("预测的降水类型：", f"{precipitation_type_translate(item['prec_type']):<3}")
            print()

lon = 116.39131  # 经度
lat = 39.90764  # 纬度
data = seventimer(lon, lat)

print_data_in_2x5_format(data)