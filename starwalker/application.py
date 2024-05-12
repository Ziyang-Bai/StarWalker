# -*- coding: utf-8 -*- 
"""
@File    :   application.py
@Time    :   2024/04/15 09:08:03
@Version :   Dev-0.0
@Desc    :   None
"""
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
import requests
import pandas
import json
import urllib.parse
import hashlib
import urllib
import time
import ephem
from datetime import datetime 
def get_moon_phase(hours_after,lat,lon):
    # 设置观察者的位置
    observer = ephem.Observer()
    observer.lat = lat  # 纬度
    observer.lon = lon  # 经度
    observer.date = datetime.now()

    # 计算x个小时后的日期
    future_date = observer.date + ephem.Date(hours_after * ephem.hour)

    # 计算月相
    moon = ephem.Moon(future_date)
    phase = moon.phase

    # 获取月相的名称
    phase_name = ephem.constellation(moon)

    return phase

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
def direction_to_int(direction_value, is_direction=True):

    """

    假设一个简单的转换逻辑，如果是方向则映射为1-4的等级，1为最不利，4为最有利。

    实际应用中需根据具体情况定义。

    """

    if is_direction:  # 假设风向，简化处理

        if direction_value in ['N', 'S']: return 2  # 北南风作为中等影响

        elif direction_value in ['E', 'W']: return 3  # 东西风稍好

        else: return 4  # 其他（如无风）视为最有利

    else:  # 对于其他参数，假设是直接的数值或已转换为有利等级

        return min(max(int(direction_value), 1), 4)  # 确保在1-4之间

def get_location_by_amap(address, key):
    url = f'https://restapi.amap.com/v3/geocode/geo?key={key}&address={address}'
    response = requests.get(url)
    data = response.json()
    if data['status'] == '1':
        lon = data['geocodes'][0]['location'].split(',')[0]
        lat = data['geocodes'][0]['location'].split(',')[1]
        return lon, lat
    else:
        return None


def weather_score(cloudcover, seeing, transparency, lifted_index, rh2m, wind10m_speed, wind10m_direction, temp2m, prec_type):

    # 根据天文观测调整权重

    weights = {

        'cloudcover': 0.25,  # 云量对观测影响大

        'seeing': 0.2,       # 视宁度次之

        'transparency': 0.2, # 透明度同样重要

        'lifted_index': 0.05, # 提升指数对天气稳定性有指示，但影响相对小

        'rh2m': 0.05,        # 相对湿度

        'wind10m_speed': 0.1, # 风速影响稳定度

        'wind10m_direction': 0.05, # 风向影响局部条件

        'temp2m': 0.05,      # 温度对观测设备操作有间接影响

        'prec_type': 0.01    # 降水类型，雨雾等会严重影响观测

    }

    

    # 转换输入为评分贡献值

    cloudcover = direction_to_int(cloudcover)

    seeing = direction_to_int(seeing)

    transparency = direction_to_int(transparency)

    lifted_index = direction_to_int(lifted_index, is_direction=False)

    rh2m = direction_to_int(rh2m, is_direction=False)

    wind10m_speed = direction_to_int(wind10m_speed, is_direction=False)

    wind10m_direction = direction_to_int(wind10m_direction)

    temp2m = direction_to_int(temp2m, is_direction=False)

    

    # 降水类型需特别处理，如晴天为最佳，其他按不利程度赋值

    if prec_type == 'none': 

        prec_type = 4

    else: 

        prec_type = 1  # 简化处理，实际可能需要更细致的分类

    

    # 计算加权总分

    total_score = sum([weights[key] * value for key, value in locals().items() if key in weights])
    if prec_type == 4:

        total_score += 0.1  # 晴天额外加分

    elif prec_type == 1:

        total_score -= 1  # 雨天减分

    if cloudcover == 9:
        total_score -= 1  # 云量大于9时减分
    elif cloudcover == 8:
        total_score -= 1
    elif cloudcover == 7:
        total_score -= 1
    elif cloudcover == 6:
        total_score -= 0.9
    elif cloudcover == 5:
        total_score -= 0.8
    elif cloudcover == 4:
        total_score -= 0.65
    elif cloudcover == 3:
        total_score -= 0.5
    elif cloudcover == 2:
        total_score -= 0.4
    elif cloudcover == 1:
        total_score += 0.5
    elif cloudcover == 0:
        total_score += 1
    

    # 返回结果

    return round(total_score, 2)
    


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
def describe_weather_condition(score):

    """

    根据天气评分返回对应的天气状况描述。

    :param score: 天气评分，范围通常是0到4。

    :return: 描述天气状况的字符串。

    """

    if 0 <= score < 0.5:

        return "糟糕"

    elif 0.5 <= score < 1.5:

        return "很差"

    elif 1.5 <= score < 2.5:

        return "较差"

    elif 2.5 <= score < 3.5:

        return "尚可"

    elif 3.5 <= score < 3.7:

        return "良好"

    elif 3.7 <= score < 3.9:

        return "很好"

    elif 3.9 <= score <= 5:

        return "极好"

    else:

        return "无效的评分，请检查输入是否在0到5之间。"
def print_data_in_line(data,lat,lon):
    if data:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("报告在" + current_time + "生成")
        for i, item in enumerate(data["dataseries"]):
            if i % 9 == 0:
                print()
            print("小时后：",       f"{item['timepoint']:<3}", end="  ")
            print(f'月相：{str(get_moon_phase(item["timepoint"],lat,lon))[:3]}', end="  ")
            print("云层覆盖：",    f"{item['cloudcover']:<3}", end="  ")
            print("视宁度：",      f"{item['seeing']:<3}", end="  ")
            print("透明度：",      f"{item['transparency']:<3}", end="  ")
            print("提升指数：",    f"{item['lifted_index']:<3}", end="  ")
            print("相对湿度：",    f"{item['rh2m']:<3}", end="  ")
            print("风速：",        f"{item['wind10m']['speed']:<3}", end="  ")
            print("风向：",        f"{direction_fullname(item['wind10m']['direction']):<3}", end="  ")
            print("温度：",        f"{item['temp2m']:<3}", end="  ")
            print("预测的降水类型：", f"{precipitation_type_translate(item['prec_type']):<3}")
            wttrs = weather_score(item['cloudcover'], item['seeing'], item['transparency'], item['lifted_index'], item['rh2m'], item['wind10m']['speed'], item['wind10m']['direction'], item['temp2m'], item['prec_type'])
            angle = get_moon_phase(item["timepoint"],lat,lon)
            if angle < 1:
                phase = "新月"
                St = 0
            elif angle < 45:
                phase = "蛾眉月"
                St = 0.5
            elif angle < 90:
                phase = "上弦月"
                St = 1
            elif angle < 135:
                phase = "盈凸月"
                St = 1.5
            elif angle < 180:
                phase = "满月"
                St = 2
            elif angle < 225:
                phase = "亏凸月"
                St = 1.5
            elif angle < 270:
                phase = "下弦月"
                St = 1
            elif angle < 315:
                phase = "残月"
                St = 0.5
            else:
                phase = "新月"
                St = 0
            wttrs = weather_score(item['cloudcover'], item['seeing'], item['transparency'], item['lifted_index'], item['rh2m'], item['wind10m']['speed'], item['wind10m']['direction'], item['temp2m'], item['prec_type'])
            wttrs -= St
            if wttrs < 0:
                wttrs = 0
            elif wttrs > 5:
                wttrs = 5
            else:
                wttrs = round(wttrs, 2)
                
            print("评分：",        f"{wttrs:<3}"," ",describe_weather_condition(wttrs))
            
#addr = '北京市海淀区中关村街道'  # 替换为你想要查询的地址
addr = input("请输入地址：")
key = 'a878560f304927262d5bb9876989dac4'  # 替换为你的高德地图API密钥
lon , lat = get_location_by_amap(addr, key)
print(lon,lat)
#覆写

#lon = 116.39131  # 经度
#lat = 39.90764  # 纬度
data = seventimer(lon, lat)

print_data_in_line(data,lat,lon)