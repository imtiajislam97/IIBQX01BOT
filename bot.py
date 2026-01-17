import os
import sys
import random
from datetime import datetime, timedelta
import pytz

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# ==============================
# 🐍 PYTHON VERSION INFO
# ==============================
print("Running on:", sys.version)

# ==============================
# 🔐 BOT TOKEN (ENV VARIABLE)
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN environment variable not set")

# ==============================
# 🔒 ALLOWED USERS
# ==============================
ALLOWED_USERS = {
    7116950303,
    6408755530
}

# ==============================
# 🕘 TIMEZONE (DHAKA)
# ==============================
dhaka = pytz.timezone("Asia/Dhaka")

def is_bot_disabled():
    now = datetime.now(dhaka)
    day = now.strftime("%A")
    hour = now.hour

    if (day == "Friday" and hour >= 21) or \
       (day in ["Saturday", "Sunday"] and (hour < 9 or hour >= 21)) or \
       (day == "Monday" and hour < 9) or \
       (day not in ["Saturday", "Sunday", "Friday", "Monday"] and (hour < 9 or hour >= 21)):
        return True
    return False

# ==============================
# 📊 MARKETS
# ==============================
MARKETS = [
    "EURUSD", "USDJPY", "USDCAD", "EURJPY", "EURCAD", "EURGBP", "EURCHF",
    "GBPUSD", "GBPJPY", "GBPCAD", "GBPCHF", "GBPAUD",
    "AUDUSD", "AUDJPY", "AUDCAD", "AUDCHF",
    "USDCHF", "NZDUSD", "CHFJPY", "CADJPY"
]

# ==============================
# 🧠 STATES
# ==============================
SELECT_MARKET, NUM_SIGNALS, TIME_WINDOW = range(3)

# ==============================
# 🚀 /start
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("🚫 You are not authorized to use this bot.")
        return ConversationHandler.END

    context.user_data.clear()

    if is_bot_disabled():
        await update.message.reply_text(
            "⚠️ BOT TEMPORARILY DISABLED\n"
            "⏰ Trading time restriction active"
        )
        return ConversationHandler.END

    text = "🚀 *IIB Future Signal Bot*\n\n📊 *Choose market numbers:*\n"
    for i, m in enumerate(MARKETS, start=1):
        text += f"{i}. {m}\n"

    text += "\n✍️ Example: `1,3,5`"

    await update.message.reply_text(text, parse_mode="Markdown")
    return SELECT_MARKET

# ==============================
# 📊 MARKET SELECT
# ==============================
async def select_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        indices = [int(x.strip()) - 1 for x in update.message.text.split(",")]
        selected = [MARKETS[i] for i in indices if 0 <= i < len(MARKETS)]
    except:
        selected = []

    if not selected:
        await update.message.reply_text("❌ Invalid selection. Try again.")
        return SELECT_MARKET

    context.user_data["markets"] = selected
    await update.message.reply_text("🔢 How many signals?")
    return NUM_SIGNALS

# ==============================
# 🔢 SIGNAL COUNT
# ==============================
async def num_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Enter a number")
        return NUM_SIGNALS

    context.user_data["num_signals"] = int(update.message.text)
    await update.message.reply_text("⏱ Time window (minutes)?")
    return TIME_WINDOW

# ==============================
# ⏱ SIGNAL GENERATION
# ==============================
async def time_window(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Enter a number")
        return TIME_WINDOW

    total_minutes = int(update.message.text)
    num_signals = context.user_data["num_signals"]
    markets = context.user_data["markets"]

    now = datetime.now(dhaka)
    used_times = set()
    signals = []

    for _ in range(num_signals):
        market = random.choice(markets)

        while True:
            mins = random.randint(5, total_minutes + 5)
            t = now + timedelta(minutes=mins)
            if t not in used_times:
                used_times.add(t)
                break

        direction = random.choice(["UP", "DOWN"])
        confidence = random.randint(85, 95)

        signals.append((t, market, direction, confidence))

    signals.sort(key=lambda x: x[0])

    msg = f"📊 *Signals (next {total_minutes} min)*\n\n"
    for t, m, d, c in signals:
        emoji = "🟢" if d == "UP" else "🔴"
        msg += f"{emoji} *{m}* → `{t.strftime('%I:%M %p')}` | *{d}* | {c}%\n"

    await update.message.reply_text(msg, parse_mode="Markdown")
    return ConversationHandler.END

# ==============================
# ❌ CANCEL
# ==============================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END

# ==============================
# 🧠 MAIN
# ==============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_MARKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_market)],
            NUM_SIGNALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, num_signals)],
            TIME_WINDOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, time_window)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
