import os
import time
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
    "不要問我為什麼跑步，問你自己為什麼不跑？",
    "生活常常被比喻成馬拉松，但我認為它更像短跑；長時間的艱苦工作被短暫的時刻打斷，那時我們得到機會盡可能的表現自己。─ 邁克爾·約翰遜",
    "一個沒有足夠勇氣去冒險的人，在人生中他將是一事無成。─ 穆罕穆德·阿里",
    "我們都需要目標。沒有目標，人生就很難過下去。─ 托里鮑姆",
    "痛快跑一回給你的感覺，遠遠好過於你枯坐家中、卻後悔自己沒有出去跑的感覺。─ 莎拉康杜",
    "訓練最痛苦的部分，就是一開始穿上鞋子的那一刻。─ 凱薩琳史薇哲",
    "我學到無論跑步與人生都沒有所謂失敗，只要你拒絕停下來。─ 安比·波爾富",
    "跑步時你跑第一、中間或最後都不重要。重要的是你可以說：我跑完全程了！─ 弗雷德·勒博",
    "跑步是為了找到內心的平靜，生命也是如此。─ 狄恩卡·那希斯",
    "有時你必須想知道你正在做什麼。這些年來，我已經給了自己1000個理由繼續跑步，但始終還是會回到最初的地方。─ 史蒂夫普利方坦",
    "跑步是件很簡單的事，只要你想，跑步也會提供給你深入了解它的機會。─ 比茲·斯通",
    "跑步如人生，只要不斷努力，就沒有所謂的失敗！─ 安比·波弗特",
    "當你感到疲憊時，想著為什麼當初開始。",
    "堅持不懈，才能看見真正的改變。跑馬拉松，是一場與自己的對話，不要輕易放棄。",
    "不要害怕失敗，害怕的應該是放棄。每一步，都是向堅強和勇氣致敬的證明。",
    "在汗水中，你會找到力量；在挑戰中，你會找到成長。跑步，是人生不斷超越的旅程。",
    "不要停下來，不要回頭看，只有前進的勇氣，才能到達更遠的地方。",
    "跑步是一種掌控生命的感覺。我給自己設定目標，然後去實現目標。─ 南希·格斯坦",
    "每一步都是向自己的挑戰說不，每一次汗水都是在磨練自己的意志：相信自己，你可以做到。",
    "不論起點有多遠，只要你不停地往前走，終點就會在你腳下。",
    "在跑步的路上，只要不放棄，你就會發現自己的潛力是無限的。",
    "跑步馬拉松是一種對抗自己的過程，每一次突破都是對內心強大的證明。",
    "完成馬拉松靠的不是傲氣，而是謙虛。",
    "勝利當然很偉大，但你若真想在生活中做出成就，秘訣就是學會如何失敗。─ 威爾瑪·魯道夫",
    "跑步不是為了數字，是為了那口呼吸。",
    "不管快慢，動起來就是今天的勝利。",
    "每一步都是選擇，選擇繼續就夠了。",
    "跑步讓你回到自己，不需要和任何人比較。",
    "不是每天狀態都好，但每天都可以出發。",
    "你的配速，就是最適合你的速度。",
    "跑過的路不會消失，都在你身體裡。",
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

    def val(name, idx): return elements[name][idx]["parameter"]["parameterName"]

    return {
        "date"        : (datetime.now() + timedelta(days=1)).strftime("%m/%d"),
        "wx"          : val("Wx", 2),
        "pop_day"     : int(val("PoP", 2)),   # 明天白天
        "pop_night" : int(val("PoP", 3)) if len(elements["PoP"]) > 3 else int(val("PoP", 2)),
        "min_t"       : int(val("MinT", 2)),
        "max_t"       : int(val("MaxT", 2)),
    }

def running_suggestion(pop_day, pop_night, max_t, min_t):
    max_pop = max(pop_day, pop_night)
    if max_pop > 60 and max_t > 30:
        return "又熱又有雨，今天換跑步機也是一種選擇，身體比里程重要。"
    elif max_pop > 60:
        return "降雨機率偏高，帶把傘出門，或改跑室內跑步機都好。"
    elif max_t > 30:
        return "明天高溫 {}°C，建議清晨六點前或傍晚六點後出門，補水最重要。".format(max_t)
    elif min_t < 12:
        return "明天低溫 {}°C，多穿一層，暖身操做足再出發。".format(min_t)
    elif pop_day > 40 and pop_night <= 40:
        return "白天有雨，建議傍晚出門跑，享受夜跑的涼爽！"
    elif pop_day <= 40 and pop_night > 40:
        return "晚上有雨，建議早點出門跑，把握白天好天氣！"
    else:
        return "明天天氣不錯，適合出門跑步，不用設定目標，就享受那口呼吸吧。"

def build_message(w):
    quote = random.choice(QUOTES)
    suggestion = running_suggestion(w["pop_day"], w["pop_night"], w["max_t"], w["min_t"])
    msg = "🗓️ 台北明日天氣｜" + w["date"] + "\n"
    msg += "\n"
    msg += "⛅ 天氣｜" + w["wx"] + "\n"
    msg += "🌡️ 氣溫｜" + str(w["min_t"]) + "°C ～ " + str(w["max_t"]) + "°C\n"
    msg += "\n"
    msg += "☔ 降雨機率\n"
    msg += "🌅 白天（06-18）｜" + str(w["pop_day"]) + "%\n"
    msg += "🌙 晚上（18-06）｜" + str(w["pop_night"]) + "%\n"
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
        time.sleep(1)

if __name__ == "__main__":
    w = get_taipei_tomorrow()
    send_line_message(build_message(w))
