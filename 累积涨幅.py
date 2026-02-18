import os
import pandas as pd

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
data_folder = os.path.join(desktop, "okx_futures_30d_daily")

start_date = "2026-02-12"
start_dt = pd.to_datetime(start_date)

files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

results = []

for f in files:
    symbol = f.replace(".csv", "")
    df = pd.read_csv(os.path.join(data_folder, f))
    df["ts"] = pd.to_datetime(df["ts"])

    # 只匹配日期，不匹配时间
    df_start = df[df["ts"].dt.date == start_dt.date()]
    if df_start.empty:
        print(f"{symbol} 没有 {start_date} 的数据，跳过")
        continue

    start_price = df_start.iloc[0]["close"]
    last_price = df.iloc[-1]["close"]
    cum_return = (last_price - start_price) / start_price * 100

    results.append({
        "symbol": symbol,
        "start_price": start_price,
        "last_price": last_price,
        "cum_return(%)": cum_return
    })

if not results:
    print("没有任何币有指定日期的数据！")
else:
    df_result = pd.DataFrame(results)
    df_result = df_result.sort_values("cum_return(%)", ascending=False).reset_index(drop=True)

    save_path = os.path.join(desktop, f"okx_cum_return_from_{start_date}.csv")
    df_result.to_csv(save_path, index=False)
    print("完成 ✅")
    print(df_result.head(20))
    print(f"已保存到: {save_path}")
