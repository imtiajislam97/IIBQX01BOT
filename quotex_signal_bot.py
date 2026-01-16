import random
from datetime import datetime, timedelta
from colorama import Fore, init
import pytz

init(autoreset=True)

# ==============================
# 🕘 AUTO DISABLE LOGIC (Dhaka)
# ==============================
dhaka = pytz.timezone('Asia/Dhaka')
now = datetime.now(dhaka)
day = now.strftime("%A")
hour = now.hour

# Friday 9 PM → Monday 9 AM  OR  Daily 9 PM → 9 AM
if (day == "Friday" and hour >= 21) or \
   (day in ["Saturday", "Sunday"] and (hour < 9 or hour >= 21)) or \
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
# 📊 MAIN BOT LOGIC
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

now = datetime.now(dhaka)
used_times = set()
signals = []

for _ in range(num_signals):
    m = random.choice(selected_markets)
    while True:
        rand_minute = random.randint(5, total_minutes + 5)  # starts counting 4–5 mins later
        signal_time = now + timedelta(minutes=rand_minute)
        if signal_time not in used_times:
            used_times.add(signal_time)
            break

    direction = random.choice(["UP", "DOWN"])
    confidence = random.randint(85, 95)

    signals.append((signal_time, m, direction, confidence))

# sort signals chronologically
signals.sort(key=lambda x: x[0])

# print signals
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
