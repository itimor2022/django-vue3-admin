#!/usr/bin/env python3
"""
liftban.py

读取当前目录下的 uid.list（每行一个 uid），对每个 uid 发送 PUT 请求到:
  http://td-admin.s6dqlvn.icu/v1/manager/user/liftban/{uid}/0

将 token 放在请求头中（Authorization: <token>）。

依赖: requests
  pip install requests
"""

import requests
import time
import sys
from typing import List

# ------- 配置区 -------
UID_FILE = "uid.list"
BASE_URL = "http://td-api.s6dqlvn.icu/v1/manager/user/liftban/{uid}/0"
TOKEN = "dcf0e9c7cefc447c9029b9e877f6b8b0"
HEADERS = {
    # 按你指定简单放在 header 中。若需要 Bearer 或其它格式，请替换下面的值。
    "token": TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json",
}
TIMEOUT = 10           # 每次请求超时时间（秒）
MAX_RETRIES = 3        # 请求失败重试次数
RETRY_BACKOFF = 2.0    # 重试间隔基数（秒），每次指数回退
# -----------------------

def read_uids(path: str) -> List[str]:
    uids = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s:
                    # 去掉首尾引号
                    if s.startswith('"') and s.endswith('"'):
                        s = s[1:-1]
                    uids.append(s)
    except FileNotFoundError:
        print(f"ERROR: uid 文件未找到: {path}", file=sys.stderr)
        sys.exit(2)
    return uids

def put_liftban(uid: str) -> requests.Response:
    url = BASE_URL.format(uid=uid)
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        time.sleep(1)
        try:
            resp = requests.put(url, headers=HEADERS, timeout=TIMEOUT)
            return resp
        except requests.RequestException as e:
            last_exc = e
            wait = RETRY_BACKOFF * (2 ** (attempt - 1))
            print(f"[{uid}] 请求失败（第 {attempt} 次）：{e}，{wait:.1f}s 后重试...")
            time.sleep(wait)
    # 所有重试后仍失败，抛出最后一次异常
    raise last_exc

def main():
    uids = read_uids(UID_FILE)
    if not uids:
        print("uid 列表为空，退出。")
        return

    print(f"共读取到 {len(uids)} 个 uid，开始逐个发送 PUT 请求...")
    success = 0
    fail = 0

    for idx, uid in enumerate(uids, start=1):
        print(f"[{idx}/{len(uids)}] uid={uid} -> ", end="", flush=True)
        try:
            resp = put_liftban(uid)
        except Exception as e:
            print(f"请求失败（网络/异常）：{e}")
            fail += 1
            continue

        # 根据返回码判断成功与否（常见 2xx 为成功）
        if 200 <= resp.status_code < 300:
            print(f"成功 (HTTP {resp.status_code})")
            success += 1
        else:
            # 打印返回体的简短信息便于排查
            body = resp.text
            snippet = body[:200].replace("\n", " ")
            print(f"失败 (HTTP {resp.status_code}) 返回: {snippet}")
            fail += 1

    print("=" * 60)
    print(f"完成：成功 {success}，失败 {fail}，总计 {len(uids)}")

if __name__ == "__main__":
    main()
