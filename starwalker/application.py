# -*- coding: utf-8 -*-
"""
@File    :   application.py
@Time    :   2024/04/15 09:08:03
@Version :   Dev-0.0
@Desc    :   None
@Branch  :   Feature-Forward
"""
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
AUTHOR = "JINGJIAN"
BRATCH = "LegacyGUI"
VERSION = "Alpha-24w01a>userdebug:Rv0.1L"
COMPILED = "TRUE"
if AUTHOR == "" or AUTHOR is None:
    AUTHOR = "JINGJIAN"
if BRATCH == "" or BRATCH is None:
    BRATCH = "Unknown"
if VERSION == "" or VERSION is None:
    VERSION = "Unknown"
if COMPILED == "" or COMPILED is None:
    COMPILED = "FALSE"
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


def direction_to_int(direction_value, is_direction=True):
    """

    假设一个简单的转换逻辑，如果是方向则映射为1-4的等级，1为最不利，4为最有利。

    实际应用中需根据具体情况定义。

    """

    if is_direction:  # 假设风向，简化处理

        if direction_value in ['N', 'S']:
            return 2  # 北南风作为中等影响

        elif direction_value in ['E', 'W']:
            return 3  # 东西风稍好

        else:
            return 4  # 其他（如无风）视为最有利

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
    if code == 100:
        print('继续')
    elif code == 101:
        print('切换协议')
    elif code == 200:
        print('成功')
    elif code == 201:
        print('创建')
    elif code == 202:
        print('已接受')
    elif code == 203:
        print('非权威信息')
    elif code == 204:
        print('无内容')
    elif code == 205:
        print('重置内容')
    elif code == 206:
        print('部分内容')
    elif code == 300:
        print('多重选择')
    elif code == 301:
        print('永久移动')
    elif code == 302:
        print('找到')
    elif code == 303:
        print('查看其他')
    elif code == 304:
        print('未修改')
    elif code == 307:
        print('临时重定向')
    elif code == 308:
        print('永久重定向')
    elif code == 400:
        print('错误请求')
    elif code == 401:
        print('未授权')
    elif code == 403:
        print('禁止')
    elif code == 404:
        print('未找到')
    elif code == 405:
        print('方法不允许')
    elif code == 406:
        print('不可接受')
    elif code == 407:
        print('代理授权 required')
    elif code == 408:
        print('请求超时')
    elif code == 409:
        print('冲突')
    elif code == 410:
        print('已删除')
    elif code == 411:
        print('长度 required')
    elif code == 412:
        print('前置条件失败')
    elif code == 413:
        print('负载过大')
    elif code == 414:
        print('URI过长')
    elif code == 415:
        print('不支持的媒体类型')
    elif code == 416:
        print('范围不可满足')
    elif code == 417:
        print('期望失败')
    elif code == 500:
        print('内部服务器错误')
    elif code == 501:
        print('未实现')
    elif code == 502:
        print('无效的网关 常见故障 请重试')
    elif code == 503:
        print('服务不可用')
    elif code == 504:
        print('网关超时')
    elif code == 505:
        print('HTTP版本不受支持')
    else:
        print('未知状态码')
    print("请联系开发者以获取帮助")
    return None


def seventimer(lon, lat):
    url = "http://www.7timer.info/bin/astro.php"
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

    eg.msgbox(content, "StarWalker")
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
    eg.msgbox(
        f"欢迎使用StarWalker星行者\n分支：{BRATCH}\n版本：{VERSION}\n作者：{AUTHOR}\n编译：{COMPILED}",
        image="starwalker - Copy.bmp")
    # addr = '北京市海淀区中关村街道'  # 替换为你想要查询的地址
    print("StarWalker 星行者")
    print("分支 ", BRATCH)
    print("版本 ", VERSION)
    print("作者 ", AUTHOR)
    print("编译 ", COMPILED)
    choicen = eg.choicebox("请选择查询方式", choices=["使用IP定位", "使用经纬度定位", "使用地址定位"])
    if choicen == "使用经纬度定位":
        lat = input("请输入纬度：")
        if lat == "" or abs(lat) > 90:
            print("输入错误")
            exit()
        lon = input("请输入经度：")
        if lon == "" or abs(lon) > 180:
            print("输入错误")
            exit()
    elif choicen == "使用IP定位":
        pubilc_ip = get_pubilc_ip()
        print(pubilc_ip)
        lon, lat = get_geolocation(pubilc_ip)
        print(lon, lat)
    else:
        key = 'a878560f304927262d5bb9876989dac4'  # 替换为你的高德地图API密钥
        lon, lat = get_location_by_amap(addr, key)
        print(lon, lat)
    curve_ask = eg.boolbox("是否要生成曲线图？", "StarWalker")
    if curve_ask:
        curve = True
    else:
        curve = False
    ask_starchart = eg.boolbox("是否要生成星图？", "StarWalker")

    # 覆写

    # lon = 116.39131  # 经度
    # lat = 39.90764  # 纬度
    if ask_starchart:
        starchart(lat, lon)
    data = seventimer(lon, lat)

    make_report(data, lat, lon, curve)
    image = Image.open(image_path)
    eg.msgbox(
        image=image_path,
        title="StarWalker - 星行者-图像预览",
        msg=time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime()) +
        "的星图")
