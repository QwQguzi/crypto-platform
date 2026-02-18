import os
import requests
import pandas as pd
import time

BASE_URL = "https://www.okx.com"

# =====================
# 创建保存路径
# =====================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
save_folder = os.path.join(desktop, "okx_futures_30d_daily")
os.makedirs(save_folder, exist_ok=True)

print("保存路径:", save_folder)

# =====================
# 获取所有USDT永续合约
# =====================
url = f"{BASE_URL}/api/v5/public/instruments"
params = {"instType": "SWAP"}

response = requests.get(url, params=params)
data = response.json()

if data["code"] != "0":
    print("接口错误:", data)
    exit()

symbols = [
    s["instId"]
    for s in data["data"]
    if s["settleCcy"] == "USDT"
]

print("合约数量:", len(symbols))

# =====================
# 下载函数（日线）
# =====================
def get_daily_klines(symbol):
    url = f"{BASE_URL}/api/v5/market/history-candles"
    params = {
        "instId": symbol,
        "bar": "1D",
        "limit": 30  # 只抓最近30根K线
    }
    r = requests.get(url, params=params).json()
    return r

# =====================
# 开始下载
# =====================
for symbol in symbols:
    try:
        print("下载:", symbol)

        data = get_daily_klines(symbol)

        if data["code"] != "0":
            print("失败:", symbol)
            continue

        df = pd.DataFrame(data["data"], columns=[
            "ts","open","high","low","close","volume",
            "volCcy","volCcyQuote","confirm"
        ])

        if df.empty:
            continue

        # 转成datetime，避免FutureWarning
        df["ts"] = pd.to_datetime(pd.to_numeric(df["ts"]), unit="ms")
        df = df.sort_values("ts").reset_index(drop=True)

        file_path = os.path.join(save_folder, f"{symbol}.csv")
        df.to_csv(file_path, index=False)

        time.sleep(0.1)  # 防止请求太快

    except Exception as e:
        print("错误:", symbol, e)

print("全部完成 ✅")
