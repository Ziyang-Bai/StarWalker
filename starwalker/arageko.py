import math
from skyfield.api import load
print("阿拉戈克 24w30a v1.0")
print("项目Github仓库：github.com/ziyang-bai/starwalker")
print("该程序根据 Mozilla 公共许可证版本 2.0 发布。")
print("加载星历数据")
planets = load('de422.bsp')
print("完成")
print("开始天体计算")
ts = load.timescale()
earth = planets['earth']
event=[]#不同天体不同状态对应的天象名称
event.append({1:"下弦月",2:"新　月",3:"满　月",4:"上弦月"})#月亮
event.append({1:"西大距",2:"上　合",3:"东大距",4:"下　合"})#地内行星
event.append({2:"西方照",4:"上　合",1:"冲  日",3:"东方照"})#地外行星，是太阳在追行星，即太阳的黄经慢慢靠近行星
delt_t1=0.5#停止迭代的时间阈值，设为1秒
delt_t2=0.05#用于判断t和t+0.05秒后的状态，两个时间差值小于0.05秒skyfield可能会比较不出差距，或者大小判断会出错,而且delt_t2要比delt_t1小一个量级左右，否则也可能出错
#设置数字对应的天体名称
'''0 SOLAR SYSTEM BARYCENTER, 1 MERCURY BARYCENTER, 2 VENUS BARYCENTER, 3 EARTH BARYCENTER, 4 MARS BARYCENTER,
5 JUPITER BARYCENTER, 6 SATURN BARYCENTER, 7 URANUS BARYCENTER, 8 NEPTUNE BARYCENTER, 9 PLUTO BARYCENTER,
10 SUN, 199 MERCURY, 299 VENUS, 301 MOON, 399 EARTH'''
body={0:"太阳系质心",1:"水星",2:"金星",3:"地球质心",4:"火星",5:"木星",6:"土星",7:"天王星",8:"海王星",9:"冥王星",10:"日",301:"月",399:"地球"}
#二分法迭代求天象时间
def iteration(jd,m,n,sta):#jd：要求的开始时间，m，n：上面不同天体的代号，sta：不同的状态函数
    s1=sta(jd,m,n)#初始状态
    s0=s1
    dt=7.0#初始时间改变量设为7天,7天足够小于两个天象之间发生的时间(还可以修改)
    while True:
        jd=ts.tdb_jd(jd.tdb+dt)#改变时间
        s=sta(jd,m,n)
        if s0!=s:
            s0=s
            dt=-dt/2#使时间改变量折半减小
        if abs(dt)<delt_t1/86400.0 and s!=s1:#s!=s1是为了让求得的时间在天象发生之后
            break
    return jd
#计算视赤道坐标和视黄道坐标
def celestial_coor(jd,n):
    apparent=earth.at(jd).observe(planets[n]).apparent()
    lon, lat, distance = apparent.radec(epoch='date')#求太阳的视赤经视赤纬和距离（epoch设为所求时间）
    e_lat, e_lon, e_distance = apparent.ecliptic_latlon(epoch='date')#求太阳的视黄纬视黄经和距离（epoch设为所求时间）
    return e_lon._degrees*math.pi/180.0,e_lat._degrees*math.pi/180.0,lon._degrees*math.pi/180.0,lat._degrees*math.pi/180.0#返回天体的视赤经/黄经和视赤纬/黄纬，单位为弧度
#给定两个黄经/赤经a1和a2，判断a2在a1的哪一侧，东（设为0）或者西（设为1）
def east_west_angle(a1,a2):
    #print("太阳黄经：{0}".format(a1*180/math.pi))
    #print("行星黄经：{0}".format(a2*180/math.pi))
    if abs(a1-a2)<math.pi:#意味着两个天体之间没有跨越黄经0点
        if a2<a1:
            return 1
        else:
            return 0
    else:
        if a2<a1:
            return 0
        else:
            return 1
#根据黄经/赤经判断天体n在天体m的哪一侧，东（设为0）或者西（设为1）(分为使用黄经判断（两个天体有一个是太阳）或者赤经判断（两个都不是太阳）)
def east_west(jd,m,n):
    if m==10 or n==10:#两个天体中有一个为太阳，则使用黄经作为判断依据
        a1=celestial_coor(jd,10)#a1设置为太阳的坐标,因为east_west_angle函数是a2的黄经相对于a1的黄经
        if m==10:
            a2=celestial_coor(jd,n)
        else:
            a2=celestial_coor(jd,m)
        return east_west_angle(a1[0],a2[0])
    else:#两个天体都不是太阳，使用赤经作为判断依据
        a1=celestial_coor(jd,m)
        a2=celestial_coor(jd,n)
        return east_west_angle(a1[2],a2[2])#若是要使用黄经，在这里把2改为0
#计算两个天体之间的夹角（使用黄道坐标或者赤道坐标计算结果应该基本相同
def included_angle(jd,m,n):
    a1=celestial_coor(jd,m)
    a2=celestial_coor(jd,n)
    a=math.acos(math.sin(a1[1])*math.sin(a2[1])+math.cos(a1[1])*math.cos(a2[1])*math.cos(a2[0]-a1[0]))#黄道坐标
    #a=math.acos(math.sin(a1[3])*math.sin(a2[3])+math.cos(a1[3])*math.cos(a2[3])*math.cos(a2[2]-a1[2]))#赤道坐标
    return a
#求两个天体之间的赤经/黄经差绝对值
def lon_angle(jd,m,n,k):#k==0使用黄经，k==其他值使用赤经
    a1=celestial_coor(jd,m)
    a2=celestial_coor(jd,n)
    if k==0:
        lon1=a1[0]
        lon2=a2[0]
    else:
        lon1=a1[2]
        lon2=a2[2]
    if abs(lon1-lon2)<math.pi:#意味着两个天体之间没有跨越赤经/黄经0点
        return abs(lon1-lon2)
    else:
        return 2*math.pi-abs(lon1-lon2)
#判断两个天体之间夹角在增大还是减小（地内行星求大距）或者是两个天体之间黄经之差是否大于90度（地外行星或者月亮求黄经差值）
def dangle(jd,m,n):#有一个天体是太阳，顺序无所谓
    if m==1 or n==1 or m==2 or n==2:#通过1秒后两个天体之间的夹角，和现在夹角之差，来判断天体之间的夹角增大还是减小
        a1=included_angle(jd,m,n)*180.0/math.pi#此刻夹角,转为角度值比弧度值更利于下面的比较，因为精度更高
        a2=included_angle(ts.tdb_jd(jd.tdb+delt_t2/86400),m,n)*180.0/math.pi#0.0001秒后夹角
        e1=lon_angle(jd,m,n,0)*180.0/math.pi#此刻黄经差
        e2=lon_angle(ts.tdb_jd(jd.tdb+delt_t2/86400),m,n,0)*180.0/math.pi#0.0001秒后黄经差
        #print(a1,a2,a1-a2)
        if a1>10.0:#二者夹角大于10°（10°足够小于最小的水星大距角度）意味着不在上合/下合附近，使用夹角判断
            if a1<a2:#夹角在增大
                return 1
            else:#夹角在减小
                return 0
        else:#二者夹角小于10°，使用黄经差判断
            if e1<e2:#黄经差值在增大
                return 1
            else:#黄经差值在减小
                return 0
    else:#两个天体之间黄经之差是否大于90度
        d=lon_angle(jd,m,n,0)
        if d>math.pi/2:#地外行星或者月亮和太阳的黄经之差绝对值大于90度
            return 1
        else:#地外行星或者月亮和太阳的黄经之差绝对值小于90度
            return 0
#判断天体所处的状态
def status(jd,m,n):
    ew=east_west(jd,m,n)
    da=dangle(jd,m,n)
    if m==10 or n==10:#有一个天体是太阳，使用黄经判断
        if ew==1 and da==1:
            return 1#地内行星：处于下合到西大距之间，地外行星：处于冲日到西方照之间，月亮：处于满月到下弦月之间
        elif ew==1 and da==0:
            return 2#地内行星：处于西大距到上合之间，地外行星：处于西方照到上合之间，月亮：处于下弦月到新月之间
        elif ew==0 and da==1:
            return 3#地内行星：处于上合到东大距之间，地外行星：处于东方照到冲日之间，月亮：处于上弦月到满月之间
        elif ew==0 and da==0:
            return 4#地内行星：处于东大距到下合之间，地外行星：处于上合到东方照之间，月亮：处于新月到上弦月之间
    else:#两个都不是，就是用赤经求合发生的时间
        return ew
#计算天体n在jd时间时的下个天象（上合/新月、下合/冲/满月、东大距/东方照/上弦月、西大距/西方照/下弦月）的时间
def next_astro_phenomenon(jd,m,n):
    return iteration(jd,m,n,status)
#求未来多次天体处于特殊几何位置的时间
def event_time(jd,m,n,num):#分别输入时间（ephem儒略日），天体，要计算的接下来要发生的天象个数
    if m==10 or n==10:#有一个天体是太阳，使用黄经判断
        if m==10:#不是太阳的另外一个天体的对应的数字
            b=n
        else:
            b=m
        #找到对应的天象名称
        if m==301 or n==301:#月亮
            i=0
        elif m==1 or n==1 or m==2 or n==2:#地内行星
            i=1
        else:#地外行星
            i=2
        for k in range(num):
            s=status(jd,m,n)
            jd=next_astro_phenomenon(jd,m,n)
            t1=ts.tdb_jd(jd.tdb+1/3)
            if i==0:
                 print("{0}：".format(event[i][s]),t1.utc_strftime(format='%Y-%m-%d %H:%M:%S'))
            elif i==1 and (s==1 or s==3):#地内行星东大距或者西大距时输出和太阳夹角
                a=included_angle(jd,m,n)*180.0/math.pi
                print("{0}{1}：".format(body[b], event[i][s]),t1.utc_strftime(format='%Y-%m-%d %H:%M:%S'),' 夹角：',a)
            else:
                 print("{0}{1}：".format(body[b], event[i][s]),t1.utc_strftime(format='%Y-%m-%d %H:%M:%S'))
    else:#天体之间的合
        print("{0}合{1}时间".format(body[m],body[n]))
        for k in range(num):
            while True:
                jd=next_astro_phenomenon(jd,m,n)
                l=lon_angle(jd,m,n,1)*180/math.pi#判断行星和月亮黄经差值,next_conjunction结果会为0°或者180°
                if l<1.0:#l<1.0代表计算的结果是天体之间赤经/黄经差值为0°左右，否则需要继续计算，下一次就是合时间（）
                    break
            a=included_angle(jd,m,n)*180.0/math.pi
            t1=ts.tdb_jd(jd.tdb+1/3)
            print(t1.utc_strftime(format='%Y-%m-%d %H:%M:%S'),' 夹角：',a)
#判断天体是否处于逆行状态,根据赤经判断天体n 1秒后在之前位置的哪一侧，东（顺行，设为0）或者西（逆行，设为1）
def retrograde(jd,m,n):#只计算n，因为逆行只涉及一个天体，为了使用iteration函数，加了一个天体m
    a1=celestial_coor(jd,n)
    a2=celestial_coor(ts.tdb_jd(jd.tdb+delt_t2/86400),n)
    return east_west_angle(a1[2],a2[2])#使用赤经判断逆行，和使用黄经判断时间略有不同
#求下次逆行或者顺行的开始时间
def next_retrograde(jd,n):
    return iteration(jd,0,n,retrograde)
#求未来多次逆行或者顺行开始时间
def retrograde_time(jd,n,num):#jd:时间，n：计算的天体代号，num：计算的次数
    s=retrograde(jd,0,n)#初始状态
    if s==0:
        print("此刻{0}{1}在顺行".format(ts.tdb_jd(jd.tdb+1/3).utc_strftime(format='%Y-%m-%d %H:%M:%S'),body[n]))
    else:
        print("此刻{0}{1}在逆行".format(ts.tdb_jd(jd.tdb+1/3).utc_strftime(format='%Y-%m-%d %H:%M:%S'),body[n]))
    for i in range(num):
        s=retrograde(jd,0,n)
        jd=next_retrograde(jd,n)
        if s==0:
            print("{0}逆行开始时间：".format(body[n]),ts.tdb_jd(jd.tdb+1/3).utc_strftime(format='%Y-%m-%d %H:%M:%S'))
        else:
            print("{0}逆行结束时间：".format(body[n]),ts.tdb_jd(jd.tdb+1/3).utc_strftime(format='%Y-%m-%d %H:%M:%S'))
jd=ts.now()
#jd= ts.tt(2020, 12, 29, 20, 51,30)#不想从当前时间开始计算，也可以指定时间开始计算
event_time(jd,5,6,3)#计算未来3次的木星合土星时间
event_time(jd,2,301,4)#计算未来4次的金星合月时间
event_time(jd,2,10,5)#计算未来5次的金星相关的天象时间
event_time(jd,4,10,6)#计算未来6次的火星相关的天象时间
event_time(jd,301,10,6)#计算未来7次的月相相关的天象时间
retrograde_time(jd,1,8)#计算未来8次的水星逆行开始或者结束时间
