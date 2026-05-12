import os
import requests
from datetime import datetime, timedelta

CWA_API_KEY   = os.environ["CWA_API_KEY"]
LINE_TOKEN    = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_GROUP_ID = os.environ["LINE_GROUP_ID"]

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
    issues = []
    if pop > 40: issues.append(f"降雨機率 {pop}%")
    if max_t > 30: issues.append(f"最高氣溫 {max_t}°C")
    if len(issues) >= 2:
        return f"⚠️ 不建議戶外跑步：{'、'.join(issues)}，建議改為室內訓練。"
    elif pop > 40:
        return f"🌧️ 留意降雨（{pop}%），建議攜帶雨具或選有頂棚跑道。"
    elif max_t > 30:
        return f"🌡️ 高溫注意（{max_t}°C），建議清晨或傍晚出發，多補水。"
    else:
        return f"✅ 天氣適合跑步！（{min_t}–{max_t}°C，降雨機率 {pop}%）出發吧！"

def build_message(w):
    return (
        f"🗓️ 台北明日天氣｜{w['date']}\n"
        f"{'─'*22}\n"
        f"🌤️  天氣：{w['wx']}\n"
        f"🌡️  氣溫：{w['min_t']}°C ～ {w['max_t']}°C\n"
        f"☔  降雨機率：{w['pop']}%\n"
        f"{'─'*22}\n"
        f"🏃  跑步建議\n"
        f"{running_suggestion(w['pop'], w['max_t'], w['min_t'])}\n"
        f"{'─'*22}\n"
        f"📡 資料來源：中央氣象署"
    )

def send_line_message(text):
    r = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"},
        json={"to": LINE_GROUP_ID, "messages": [{"type": "text", "text": text}]},
        timeout=10
    )
    print("✅ 送出成功" if r.status_code == 200 else f"❌ 失敗：{r.status_code} {r.text}")

if __name__ == "__main__":
    w = get_taipei_tomorrow()
    send_line_message(build_message(w))
