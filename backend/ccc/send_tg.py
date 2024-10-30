import telegram
import requests

chat_id = "-4591709428"
token = "7114302389:AAHaFEzUwXj7QC1A20qwi_tJGlkRtP6FOlg"
bot = telegram.Bot(token=token)


def send_message(msg):
    """
    Send a message to a telegram user or group specified on chatId
    chat_id must be a number!
    """
    # bot = telegram.Bot(token=token)
    # bot.sendMessage(chat_id=chat_id, text=msg)
    # print('Message Sent!')
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}"
    r = requests.get(url)
    print(r)



if __name__ == '__main__':
    msg = "你好"
    send_message(msg)
