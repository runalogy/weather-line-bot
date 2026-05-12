import os
import requests
import random
from datetime import datetime, timedelta

CWA_API_KEY   = os.environ["CWA_API_KEY"]
LINE_TOKEN    = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]

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
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": CWA_API_KEY,
        "locationName" : "臺北市",
        "elementName"  : "Wx,PoP,MinT,MaxT",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    location = data["records"]["location"][0]
    elements = {e["elementName"]: e["time"] for e in location["weatherElement"]}
    idx = 2
    def val(name): return elements[name][idx]["parameter"]["parameterName"]
    return {
        "date"  : (datetime.now() + timedelta(days=1)).strftime("%m/%d"),
        "wx"    : val("Wx"),
        "pop"   : int(val("PoP")),
        "min_t" : int(val("MinT")),
        "max_t" : int(val("MaxT")),
    }

def running_suggestion(pop, max_t, min_t):
    if pop > 40 and max_t > 30:
        return "⚠️ 又熱又有雨，今天換跑步機也是一種選擇，身體比里程重要。"
    elif pop > 40:
        return f"🌧️ 降雨機率 {pop}%，帶把傘出門，或改跑室內跑步機都好。"
    elif max_t > 30:
        return f"🌡️ 明天高溫 {max_t}°C，建議清晨六點前或傍晚六點後出門，慢一點沒關係，補水最重要。"
    elif min_t < 12:
        return f"🧣 明天低溫 {min_t}°C，多穿一層，暖身操做足再出發，身體要顧好。"
    else:
        return "✅ 明天天氣不錯，適合出門跑步，不用設定目標，就享受那口呼吸吧。"

def build_message(w):
    quote = random.choice(QUOTES)
    return (
        f"🗓️ 台北明日天氣｜{w['date']}\n"
        f"\n"
        f"⛅
