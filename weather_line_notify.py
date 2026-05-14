import os
import requests
import random
from datetime import datetime, timedelta

CWA_API_KEY = os.environ["CWA_API_KEY"]
LINE_TOKEN  = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]

GROUP_IDS = [
    os.environ.get("LINE_GROUP_ID", ""),
    os.environ.get("LINE_GROUP_ID_2", ""),
    os.environ.get("LINE_GROUP_ID_3", ""),
    os.environ.get("LINE_GROUP_ID_4", ""),
]

QUOTES = [
    "跑步不是為了數字，是為了那口呼吸。",
    "不管快慢，動起來就是今天的勝利。",
    "每一步都是選擇，選擇繼續就夠了。",
    "跑步讓你回到自己，不需要和任何人比較。",
    "不是每天狀態都好，但每天都可以出發。",
    "你的配速，就是最適合你的速度。",
    "跑過的路不會消失，都在你身體裡。",
    "今天跑步，不是為了變更好，是因為你值得。",
    "少一點比較，多一點呼吸，跑步會更快樂。",
    "把鞋穿上，其他的路會自己走出來。",
]

def get_taipei_tomorrow():
    # F-D0047-061 逐三小時預報
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061"
    params = {
        "Authorization": CWA_API_KEY,
        "locationName" : "臺北市",
        "elementName"  : "PoP6h,T,Wx",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    location = data["records"]["locations"][0]["location"][0]
    elements = {e["elementName"]: e["time"] for e in location["weatherElement"]}

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # 找明天的資料
    def get_period(elem, start_hour):
        for t in elements[elem]:
            t_start = t["startTime"]
            if tomorrow in t_start and "T{:02d}".format(start_hour) in t_start:
                v = t.get("elementValue", [{}])
                return v[0].get("value", "N/A")
        return "N/A"

    # 早上 06:00, 下午 12:00, 晚上 18:00
    pop_morning   = get_period("PoP6h", 6)
    pop_afternoon = get_period("PoP6h", 12)
    pop_evening   = get_period("PoP6h", 18)

    temp_morning   = get_period("T", 6)
    temp_afternoon = get_period("T", 12)
    temp_evening   = get_period("T", 18)

    wx_morning = get_period("Wx", 6)

    # 最高最低氣溫
    temps = []
    for v in [temp_morning, temp_afternoon, temp_evening]:
        try:
            temps.append(int(v))
        except:
            pass

    return {
        "date"          : (datetime.now() + timedelta(days=1)).strftime("%m/%d"),
        "wx"            : wx_morning if wx_morning != "N/A" else "天氣資料未取得",
        "min_t"         : min(temps) if temps else 0,
        "max_t"         : max(temps) if temps else 0,
        "pop_morning"   : pop_morning,
        "pop_afternoon" : pop_afternoon,
        "pop_evening"   : pop_evening,
    }

def running_suggestion(pop_m, pop_a, pop_e, max_t, min_t):
    max_pop = max(
        int(pop_m) if str(pop_m).isdigit() else 0,
        int(pop_a) if str(pop_a).isdigit() else 0,
        int(pop_e) if str(pop_e).isdigit() else 0,
    )
    if max_pop > 60 and max_t > 30:
        return "又熱又有雨，今天換跑步機也是一種選擇，身體比里程重要。"
    elif max_pop > 60:
        return "降雨機率偏高，帶把傘出門，或改跑室內跑步機都好。"
    elif max_t > 30:
        return "明天高溫 {}°C，建議清晨六點前或傍晚六點後出門，補水最重要。".format(max_t)
    elif min_t < 12:
        return "明天低溫 {}°C，多穿一層，暖身操做足再出發。".format(min_t)
    elif int(pop_a) > 40 if str(pop_a).isdigit() else False:
        return "下午有雨，建議早上出門跑，享受清晨的空氣！"
    else:
        return "明天天氣不錯，適合出門跑步，不用設定目標，就享受那口呼吸吧。"

def build_message(w):
    quote = random.choice(QUOTES)
    suggestion = running_suggestion(
        w["pop_morning"], w["pop_afternoon"], w["pop_evening"],
        w["max_t"], w["min_t"]
    )
    msg = "🗓️ 台北明日天氣｜" + w["date"] + "\n"
    msg += "\n"
    msg += "⛅ 天氣｜" + w["wx"] + "\n"
    msg += "🌡️ 氣溫｜" + str(w["min_t"]) + "°C ～ " + str(w["max_t"]) + "°C\n"
    msg += "\n"
    msg += "☔ 降雨機率\n"
    msg += "🌅 早上（06-12）｜" + str(w["pop_morning"]) + "%\n"
    msg += "☀️ 下午（12-18）｜" + str(w["pop_afternoon"]) + "%\n"
    msg += "🌙 晚上（18-24）｜" + str(w["pop_evening"]) + "%\n"
    msg += "\n"
    msg += "🏃 跑步建議\n"
    msg += suggestion + "\n"
    msg += "\n"
    msg += "💬 今日心靈\n"
    msg += quote + "\n"
    msg += "\n"
    msg += "📡 Runalogy｜每日為你播報"
    return msg

def send_line_message(text):
    for gid in GROUP_IDS:
        if not gid:
            continue
        r = requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + LINE_TOKEN},
            json={"to": gid, "messages": [{"type": "text", "text": text}]},
            timeout=10
        )
        if r.status_code == 200:
            print("送出成功：" + gid[:10])
        else:
            print("失敗：" + str(r.status_code))

if __name__ == "__main__":
    w = get_taipei_tomorrow()
    send_line_message(build_message(w))
