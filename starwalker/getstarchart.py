import requests
import bs4
from bs4 import BeautifulSoup
import time
def starchart(lat, lon,utctime):
    url = "http://fourmilab.net/cgi-bin/Yoursky"
    #UTCtime format <Year>/<Month>/<Day> <Hour>:<Minute>:<Second>
    params = {
        "date": "1",
        "utc":utctime,
        "lat": lat + "%B0",
        "lon": lon + "%B0",
        "ns":"North",
        "ew":"East",
        "deepm": "2.5",
        "consto": "on",
        "liamg":"5.5",
        "starnm":"1",
        "starbm":"5",
        "fontscale":"1.0",
        "scheme":"3",
        "imgsize": "1000",
        "elements": ""}

    for i in range(5):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            print(soup)
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
starchart("0", "0", "2023/10/1 12:00:00")