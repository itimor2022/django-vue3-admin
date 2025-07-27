import requests

# 替换成你的 Bot Token
BOT_TOKEN = "7114302389:AAHaFEzUwXj7QC1A20qwi_tJGlkRtP6FOlg"


def get_chat_id():
    # 获取 Bot 的最新消息
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url).json()

    if not response["ok"] or not response["result"]:
        print("请先给你的 Bot 发送一条消息！")
        return None

    # 提取最新的 Chat ID
    latest_update = response["result"][-1]
    chat_id = latest_update["message"]["chat"]["id"]
    print(f"你的 Chat ID 是: {chat_id}")
    return chat_id


get_chat_id()