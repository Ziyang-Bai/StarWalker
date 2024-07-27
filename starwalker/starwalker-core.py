# -*- coding: utf-8 -*-
import os
from datetime import datetime
from PIL import Image
import easygui as eg
from bs4 import BeautifulSoup
import matplotlib
import matplotlib.pyplot as plt
import ephem
import time
import urllib
import hashlib
import urllib.parse
import json
import pandas
import requests
from skyfield.framelib import ecliptic_frame
from skyfield.api import load
image_path = ".\\star_map.png"
matplotlib.rc("font", family='Microsoft YaHei')
def get_moon_phase(hours_after, lat, lon):
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


def get_geolocation(ip_addr):
    url = "https://get.geojs.io/v1/ip/geo.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['longitude'], data['latitude']


def get_pubilc_ip():
    url = "http://ipinfo.io/ip"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip()
    else:
        return None


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
    if '{0:.1f}'.format(phase) == 0:
        return True
    else:
        return False


def geodata():
    url = "http://api.geodatasource.com/city"
    params = {'key': 'YKWZWPVPQNAOJHWQSNXQ5IBGPSKXETXD',
              'format': 'json', 'lat': 37.3861, 'lng': -122.084}

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

#这个模块已弃用
def direction_to_int(direction_value, is_direction=True):
    if is_direction:
        if direction_value in ['N', 'S']:
            return 2
        elif direction_value in ['E', 'W']:
            return 3
        else:
            return 4
    else:
        return min(max(int(direction_value), 1), 4)

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


def weather_score(
        cloudcover,
        seeing,
        transparency,
        lifted_index,
        rh2m,
        wind10m_speed,
        wind10m_direction,
        temp2m,
        prec_type):
    # 根据天文观测调整权重
    weights = {

        'cloudcover': 1,  # 云量对观测影响大

        'seeing': 0.3,       # 视宁度次之

        'transparency': 0.4,  # 透明度同样重要

        'lifted_index': 0.3,  # 提升指数对天气稳定性有指示，但影响相对小

        'rh2m': -0.5,        # 相对湿度

        'wind10m_speed': -0.3,  # 风速影响稳定度

        'wind10m_direction': 0,  # 风向影响局部条件

        'temp2m': 0,      # 温度对观测设备操作有间接影响

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
    total_score = sum([weights[key] * value for key,
                       value in locals().items() if key in weights])
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
def responsecode(code):
    file_path = './/lib//i18n//zh_cn//http_status_code.json'
    try:
        with open(file_path, 'r') as file:
            descriptions = json.load(file)
        description = descriptions.get(str(code), '未知状态码')
        return description
    except FileNotFoundError:
        print("文件未找到，请检查文件路径是否正确。")
        return '未知状态码'
    except json.JSONDecodeError:
        print("JSON 解析错误，请检查文件格式是否正确。")
        return '未知状态码'
    except Exception as e:
        print(f"发生错误: {e}")
        return '未知状态码'
def seventimer(lon, lat, url):
    params = {
        "lon": lon,
        "lat": lat,
        "ac": "0",
        "unit": "metric",
        "output": "json",
        "tzshift": "0"}
    headers = {
        'Content-Type': 'application/json'
    }

    for i in range(5):
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = json.loads(response.text)
            return data
        except requests.RequestException as e:
            print(f"请求失败，重试次数：{i + 1}")
            if i < 4:
                time.sleep(2)
            else:
                raise e

def describe_weather_condition(score):
    """
    根据天气评分返回对应的天气状况描述。

    :param score: 天气评分，范围通常是0到5。

    :return: 描述天气状况的字符串。
    """
    # 定义 JSON 文件路径
    file_path = './/lib//i18n//zh_cn//weather_conditions.json'

    try:
        # 读取 JSON 文件
        with open(file_path, 'r', encoding='utf-8') as file:
            conditions = json.load(file)

        # 查找最接近的评分
        closest_score = min(conditions.keys(), key=lambda x: abs(float(x) - score))
        description = conditions[closest_score]

        # 返回描述
        return description

    except FileNotFoundError:
        print("文件未找到，请检查文件路径是否正确。")
        return '未知天气状况'
    except json.JSONDecodeError:
        print("JSON 解析错误，请检查文件格式是否正确。")
        return '未知天气状况'
    except Exception as e:
        print(f"发生错误: {e}")
        return '未知天气状况'


def make_report(data, lat, lon, graph):
    timepoint = []
    lunarphase = []
    cloudcover = []
    seeing = []
    transparency = []
    lifted_index = []
    rh2m = []
    wind10m_speed = []
    temp2m = []
    score_list = []
    if data:
        f = open("report.txt", "a", encoding="utf-8")
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("报告在" + current_time + "生成")
        f.write("报告在" + current_time + "生成\n")
        f.close()
        for i, item in enumerate(data["dataseries"]):

            if i % 9 == 0:
                print()
                f = open("report.txt", "a", encoding="utf-8")
                f.close()
            f = open("report.txt", "a", encoding="utf-8")
            print("小时后：", f"{item['timepoint']:<3}", end="  ")
            f.write("小时后：" + f"{item['timepoint']:<3}" + "  ")
            timepoint.append(item['timepoint'])
            print(
                f'月相：{str(get_moon_phase(item["timepoint"],lat,lon))[:3]}',
                end="  ")
            f.write(
                f'月相：{str(get_moon_phase(item["timepoint"],lat,lon))[:3]}' +
                "  ")
            lunarphase.append(get_moon_phase(item["timepoint"], lat, lon))
            print("云层覆盖：", f"{item['cloudcover']:<3}", end="  ")
            f.write("云层覆盖：" + f"{item['cloudcover']:<3}" + "  ")
            cloudcover.append(item['cloudcover'])
            print("视宁度：", f"{item['seeing']:<3}", end="  ")
            f.write("视宁度：" + f"{item['seeing']:<3}" + "  ")
            seeing.append(item['seeing'])
            print("透明度：", f"{item['transparency']:<3}", end="  ")
            f.write("透明度：" + f"{item['transparency']:<3}" + "  ")
            transparency.append(item['transparency'])
            print("提升指数：", f"{item['lifted_index']:<3}", end="  ")
            f.write("提升指数：" + f"{item['lifted_index']:<3}" + "  ")
            lifted_index.append(item['lifted_index'])
            print("相对湿度：", f"{item['rh2m']:<3}", end="  ")
            f.write("相对湿度：" + f"{item['rh2m']:<3}" + "  ")
            rh2m.append(item['rh2m'])
            print("风速：", f"{item['wind10m']['speed']:<3}", end="  ")
            f.write("风速：" + f"{item['wind10m']['speed']:<3}" + "  ")
            wind10m_speed.append(item['wind10m']['speed'])
            print(
                "风向：",
                f"{direction_fullname(item['wind10m']['direction']):<3}",
                end="  ")
            f.write(
                "风向：" +
                f"{direction_fullname(item['wind10m']['direction']):<3}" +
                "  ")
            print("温度：", f"{item['temp2m']:<3}", end="  ")
            f.write("温度：" + f"{item['temp2m']:<3}" + "  ")
            temp2m.append(item['temp2m'])
            print(
                "预测的降水类型：",
                f"{precipitation_type_translate(item['prec_type']):<3}")
            f.write(
                "预测的降水类型：" +
                f"{precipitation_type_translate(item['prec_type']):<3}")
            wttrs = weather_score(
                item['cloudcover'],
                item['seeing'],
                item['transparency'],
                item['lifted_index'],
                item['rh2m'],
                item['wind10m']['speed'],
                item['wind10m']['direction'],
                item['temp2m'],
                item['prec_type'])
            angle = get_moon_phase(item["timepoint"], lat, lon)
            if angle < 1:
                phase = "新月"
                St = 0
            elif angle < 45:
                phase = "蛾眉月"
                St = 0.5
            elif angle < 90:
                phase = "上弦月"
                St = 1.5
            elif angle < 135:
                phase = "盈凸月"
                St = 1.75
            elif angle < 180:
                phase = "满月"
                St = 2.5
            elif angle < 225:
                phase = "亏凸月"
                St = 1.75
            elif angle < 270:
                phase = "下弦月"
                St = 1.5
            elif angle < 315:
                phase = "残月"
                St = 0.5
            else:
                phase = "新月"
                St = 0
            if precipitation_type_translate(
                    item['prec_type']) == "雨" or precipitation_type_translate(
                    item['prec_type']) == '雪':
                St = St + 1
            wttrs = weather_score(
                item['cloudcover'],
                item['seeing'],
                item['transparency'],
                item['lifted_index'],
                item['rh2m'],
                item['wind10m']['speed'],
                item['wind10m']['direction'],
                item['temp2m'],
                item['prec_type'])

            wttrs = wttrs - St
            if wttrs < 0:
                wttrs = 0
            elif wttrs > 5:
                wttrs = 5
            else:
                wttrs = round(wttrs, 2)

            print("评分：", f"{wttrs:<3}", " ", describe_weather_condition(wttrs))
            f.write(
                "评分：" +
                f"{wttrs:<3}" +
                "  " +
                describe_weather_condition(wttrs) +
                "\n")
            f.close()
            # 使用MSGbox显示数据
            score_list.append(wttrs)
    with open("report.txt", "r", encoding="utf-8") as f:
        content = f.read()

    if graph:
        """
        timepoint = []X
        lunarphase = []X
        cloudcover = []X
        seeing = []X
        transparency = []X
        lifted_index = []
        rh2m = [] X
        wind10m_speed = []X
        temp2m = []X
        """
        # plt.plot(timepoint,lunarphase,color="blue",label="月相")
        plt.plot(timepoint, temp2m, color="red", label="气温")
        plt.plot(timepoint, rh2m, color="green", label="湿度")
        plt.plot(timepoint, wind10m_speed, color="black", label="风速")
        plt.plot(timepoint, seeing, color="orange", label="视宁度")
        plt.plot(timepoint, cloudcover, color="purple", label="云量")
        plt.plot(timepoint, transparency, color="yellow", label="透明度")
        plt.plot(timepoint, lifted_index, color="pink", label="抬升指数")
        plt.plot(timepoint, score_list, color="brown", label="观测评分")
        plt.xlabel("时间")
        plt.ylabel("数值")
        plt.title("观测数据")
        plt.legend()
        plt.show()


def starchart(lat, lon):
    url = "http://fourmilab.net/cgi-bin/uncgi/Yoursky"
    params = {
        "fov": "1",
        "lat": lat,
        "lon": lon,
        "depm": "0",
        "consto": "1",
        "imgsize": "1000",
        "moonp": "1"}

    for i in range(5):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            img_url = soup.find("img")["src"]
            img_data = requests.get("http://fourmilab.net" + img_url).content

            with open("star_map.png", "wb") as f:
                f.write(img_data)
            break
        except requests.RequestException as e:
            print(f"请求失败，重试次数：{i + 1}")
            if i < 4:
                time.sleep(2)
            else:
                raise e


if __name__ == '__main__':
    if os.path.exists("report.txt"):
        # 如果文件存在，打开文件并清空内容
        with open("report.txt", "r+", encoding="utf-8") as f:
            f.read()
            f.seek(0)
            f.truncate()
    else:
        # 如果文件不存在，创建文件
        with open("report.txt", "w", encoding="utf-8") as f:
            pass
    # 显示欢迎信息
    # addr = '北京市海淀区中关村街道'  # 替换为你想要查询的地址
    print("StarWalker 星行者")
    choicen = input("请选择查询方式"+"1使用IP定位"+"2使用经纬度定位"+"3使用地址定位")
    if choicen == "2":
        lat = input("请输入纬度：")
        if lat == "" or abs(lat) > 90:
            print("输入错误")
            exit()
        lon = input("请输入经度：")
        if lon == "" or abs(lon) > 180:
            print("输入错误")
            exit()
    elif choicen == "1":
        pubilc_ip = get_pubilc_ip()
        print(pubilc_ip)
        lon, lat = get_geolocation(pubilc_ip)
        print(lon, lat)
    else:
        addr = input("请输入地址：")
        key = 'a878560f304927262d5bb9876989dac4'  # 替换为你的高德地图API密钥
        lon, lat = get_location_by_amap(addr, key)
        print(lon, lat)
    curve_ask = input("是否要生成曲线图？"+"True/False")
    if curve_ask:
        curve = "True"
    else:
        curve = "False"
    ask_starchart = input("是否要生成星图？"+"True/False")

    # 覆写

    # lon = 116.39131  # 经度
    # lat = 39.90764  # 纬度
    if ask_starchart == "True":
        starchart(lat, lon)
    data = seventimer(lon, lat, "http://www.7timer.info/bin/astro.php")
    if curve_ask == "True":
        make_report(data, lat, lon, curve)
    eg.msgbox(
        image=image_path,
        title="StarWalker - 星行者-图像预览",
        msg=time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime()) +
        "的星图")
