import ephem
import matplotlib.pyplot as plt
from math import radians, degrees

def calculate_star_chart(observer_location, date):
    # 设置观测者的位置
    observer = ephem.Observer()
    observer.lat = observer_location[0]  # 纬度
    observer.lon = observer_location[1]  # 经度
    observer.date = date  # 观测日期

    # 定义一些常见的恒星
    stars_data = {
        'Sirius': {'RA': '06:45:08.917', 'Dec': '-16:42:58.017'},  # Sirius
        'Vega': {'RA': '18:36:56.3391', 'Dec': '+38:47:01.29'},  # Vega
        'Arcturus': {'RA': '14:15:43.0468', 'Dec': '+19:18:19.57'},  # Arcturus
        'Capella': {'RA': '05:15:52.22', 'Dec': '+46:03:43.5'},  # Capella
        'Betelgeuse': {'RA': '05:55:10.323', 'Dec': '+07:24:25.12'},  # Betelgeuse
        'Rigel': {'RA': '05:14:32.27', 'Dec': '-08:12:05.9'},  # Rigel
    }

    # 创建 FixedBody 对象并计算每个星星的位置
    star_positions = []
    for name, data in stars_data.items():
        star = ephem.FixedBody()
        star._ra = data['RA']
        star._dec = data['Dec']
        star.compute(observer)
        altitude = star.alt * 180 / ephem.pi  # 将弧度转换为度数
        azimuth = star.az * 180 / ephem.pi  # 将弧度转换为度数
        star_positions.append((name, altitude, azimuth))

    return star_positions

def plot_star_chart(star_positions):
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    # 设置极坐标轴的范围
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)  # 逆时针方向
    ax.set_rlim(0, 90)
    ax.grid(True)

    # 绘制恒星
    for name, altitude, azimuth in star_positions:
        ax.scatter(radians(90 - altitude), radians(azimuth), label=name)

    # 添加图例
    ax.legend(loc='upper right')

    # 显示图形
    plt.show()

# 示例观测位置和时间
location = ('39.970288', '116.321622')  # 费城的纬度和经度
date = '2024/7/27 17:50'  # 2024年7月27日晚上9点

# 计算星图
star_chart = calculate_star_chart(location, date)

# 绘制星图
plot_star_chart(star_chart)