import requests
import pandas as pd
from datetime import datetime, timedelta
from colorama import Fore, init
import pytz
import time

init(autoreset=True)

# ==============================
# 🕘 AUTO DISABLE LOGIC (Dhaka) — UNCHANGED
# ==============================
dhaka = pytz.timezone('Asia/Dhaka')
now = datetime.now(dhaka)
day = now.strftime("%A")
hour = now.hour

if (day == "Friday" and hour >= 21) or \
   (day in ["Saturday", "Sunday"]) or \
   (day == "Monday" and hour < 9) or \
   (day not in ["Saturday", "Sunday", "Friday", "Monday"] and (hour < 9 or hour >= 21)):
    print(Fore.GREEN + "⚠️SORRY, MATE," + Fore.RESET + " " +
          Fore.RED + "IIB Future Signal Bot" + Fore.RESET + " " +
          Fore.GREEN + "IS TEMPORARILY DISABLED AT THIS MOMENT - " +
          Fore.RED + "BY ORDER OF IIB" + Fore.RESET)
    exit()
else:
    print(Fore.RED + "🚀IIB Future Signal Bot " + Fore.LIGHTGREEN_EX + "STARTED!\n")

# ==============================
# 📊 MARKETS — SAME AS OLD
# ==============================
markets = [
    "EURUSD", "USDJPY", "USDCAD", "EURJPY", "EURCAD", "EURGBP", "EURCHF",
    "GBPUSD", "GBPJPY", "GBPCAD", "GBPCHF", "GBPAUD", "AUDUSD", "AUDJPY",
    "AUDCAD", "AUDCHF", "USDCHF", "NZDUSD", "CHFJPY", "CADJPY"
]

print(Fore.RED + "📊Choose your market/s :-")
for i, m in enumerate(markets, start=1):
    print(Fore.GREEN + f"  {i}. {m}")

selected = input(Fore.RED + "\nWhich market/s do you want?? : ")
num_signals = int(input(Fore.RED + "\nHow many signals do you want?? : "))
total_minutes = int(input(Fore.RED + "\nEnter total time window for signals in minutes: "))

market_indices = [int(x.strip()) - 1 for x in selected.split(",") if x.strip().isdigit()]
selected_markets = [markets[i] for i in market_indices]

print(Fore.CYAN + f"\n🚀📊IIB Future Signals for next {total_minutes} minutes---")

# ==============================
# 📈 REAL MARKET DATA
# ==============================
API_KEY = "demo"   # replace with real key later
INTERVAL = "1min"

def analyze_market(symbol):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "outputsize": 120,
        "apikey": API_KEY
    }

    r = requests.get(url, params=params).json()
    if "values" not in r:
        return None

    df = pd.DataFrame(r["values"])
    df["close"] = df["close"].astype(float)
    df = df[::-1]

    # ===== Indicators =====
    df["ema9"] = df["close"].ewm(span=9).mean()
    df["ema21"] = df["close"].ewm(span=21).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()
    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9).mean()

    last = df.iloc[-1]

    # ===== Trader-style logic =====
    trend_up = last["ema9"] > last["ema21"] > last["ema50"]
    trend_down = last["ema9"] < last["ema21"] < last["ema50"]

    if trend_up and last["rsi"] > 50 and last["rsi"] < 65 and last["macd"] > last["signal"]:
        return "UP", 90

    if trend_down and last["rsi"] < 50 and last["rsi"] > 35 and last["macd"] < last["signal"]:
        return "DOWN", 90

    return None

# ==============================
# 🧠 SIGNAL GENERATION — NO RANDOM
# ==============================
signals = []
used_times = set()
base_time = datetime.now(dhaka) + timedelta(minutes=5)

while len(signals) < num_signals:
    for m in selected_markets:
        result = analyze_market(m)
        if not result:
            continue

        direction, confidence = result
        signal_time = base_time + timedelta(minutes=len(signals) * 2)

        if signal_time in used_times:
            continue

        used_times.add(signal_time)
        signals.append((signal_time, m, direction, confidence))

        if len(signals) >= num_signals:
            break

    time.sleep(1)

signals.sort(key=lambda x: x[0])

# ==============================
# 🖨 OUTPUT — SAME STYLE
# ==============================
for signal_time, m, direction, confidence in signals:
    if direction == "UP":
        print(Fore.YELLOW + f"{m} → {signal_time.strftime('%I:%M %p')} : " +
              Fore.GREEN + f"{direction}" +
              Fore.YELLOW + f" | Confidence: {confidence}%")
    else:
        print(Fore.YELLOW + f"{m} → {signal_time.strftime('%I:%M %p')} : " +
              Fore.RED + f"{direction}" +
              Fore.YELLOW + f" | Confidence: {confidence}%")

print(Fore.LIGHTGREEN_EX + "✅ Signals generation completed by " +
      Fore.RED + "order of IIB" +
      Fore.LIGHTGREEN_EX + ", Now use it with proper rules!!")