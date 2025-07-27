import requests
import logging
from datetime import datetime

# 配置参数
TIMEOUT = 10  # 请求超时时间(秒)

# Telegram Bot 配置
TELEGRAM_BOT_TOKEN = "7114302389:AAHaFEzUwXj7QC1A20qwi_tJGlkRtP6FOlg"  # 你的 Telegram Bot Token
TELEGRAM_CHAT_ID = "-4807743991"  # 接收消息的 Chat ID

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='domain_monitor.log'
)


def get_last_domain_from_nginx(config_text):
    """从 Nginx 配置中提取最后一个域名"""
    # 找到 server_name 行的起始和结束位置
    server_name_start = config_text.find("server_name")
    if server_name_start == -1:
        return None

    # 从 server_name 开始找到分号结束
    server_name_end = config_text.find(";", server_name_start)
    if server_name_end == -1:
        return None

    # 提取域名部分并分割成列表
    domains_str = config_text[server_name_start + len("server_name"):server_name_end].strip()
    domains = domains_str.split()

    return domains[-1] if domains else None


def get_last_domain_from_file(file_path):
    """从 Nginx 配置文件中提取最后一个域名"""
    with open(file_path, 'r') as f:
        config_text = f.read()
    return get_last_domain_from_nginx(config_text)  # 使用方法1或2


def check_domain(domain):
    """检测域名是否可以访问"""
    schemes = ['http://', 'https://']  # 同时检查 HTTP 和 HTTPS

    for scheme in schemes:
        url = f"{scheme}{domain}"
        try:
            response = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
            return response.status_code
        except (requests.ConnectionError, requests.Timeout, requests.RequestException) as e:
            logging.warning(f"检测 {url} 失败: {str(e)}")
            continue

    return 200


def send_telegram_alert(domain, code, pan):
    """通过 Telegram Bot 发送报警消息"""
    message = (
        f"🚨 {pan} 域名监控警报 🚨\n\n"
        f"域名: {domain}\n"
        f"状态: {code}\n"
        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"请立即检查!"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logging.info(f"Telegram 报警发送成功: {domain}")
        else:
            logging.error(f"Telegram 报警发送失败: {response.text}")
    except Exception as e:
        logging.error(f"发送 Telegram 消息出错: {str(e)}")


def main():
    logging.info("域名监控服务启动...")
    last_domain = get_last_domain_from_file("/www/server/panel/vhost/nginx/qgm.dao.conf")
    print("文件中的最后一个域名:", last_domain)
    domains = [last_domain, "154.202.156.162:701/", '154.202.156.172:701/skl001']
    pan = '强国'
    for domain in domains:
        logging.info(f"正在检测 {domain}...")
        code = check_domain(domain)

        if code not in [200, 404]:
            logging.error(f"域名 {domain} 无法访问!")
            send_telegram_alert(domain, code, pan)


if __name__ == "__main__":
    main()
