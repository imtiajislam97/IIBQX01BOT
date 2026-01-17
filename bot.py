import sys
print(Python "3.11.9", sys.version)
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
# 🔐 BOT TOKEN
# ==============================
BOT_TOKEN = os.getenv(8517145371:AAGdn3rpJCz2vOpsLh7_nkrR6Rre1Vizzko)

# ==============================
# 🔒 ALLOWED USERS (ONLY THESE CAN USE)
# ==============================
ALLOWED_USERS = {
    7116950303,
    6408755530
}

# ==============================
# 🕘 AUTO DISABLE LOGIC (Dhaka)
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
# 📊 MARKETS (UNCHANGED)
# ==============================
MARKETS = [
    "EURUSD", "USDJPY", "USDCAD", "EURJPY", "EURCAD", "EURGBP", "EURCHF",
    "GBPUSD", "GBPJPY", "GBPCAD", "GBPCHF", "GBPAUD", "AUDUSD", "AUDJPY",
    "AUDCAD", "AUDCHF", "USDCHF", "NZDUSD", "CHFJPY", "CADJPY"
]

# ==============================
# 🧠 STATES
# ==============================
SELECT_MARKET, NUM_SIGNALS, TIME_WINDOW = range(3)

# ==============================
# 🚀 START (HARD RESET)
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("🚫 You are not authorized to use this bot.")
        return ConversationHandler.END

    context.user_data.clear()  # 🔥 HARD RESET

    if is_bot_disabled():
        await update.message.reply_text(
            "⚠️ SORRY, MATE,\n"
            "🚫 IIB Future Signal Bot is temporarily DISABLED\n"
            "📛 By order of IIB"
        )
        return ConversationHandler.END

    text = "🚀 *IIB Future Signal Bot STARTED!*\n\n"
    text += "📊 *Choose your market/s:*\n"

    for i, m in enumerate(MARKETS, start=1):
        text += f"{i}. {m}\n"

    text += "\n✍️ Send market numbers (comma-separated)\nExample: `1,3,5`"

    await update.message.reply_text(text, parse_mode="Markdown")
    return SELECT_MARKET

# ==============================
# 📊 MARKET SELECTION
# ==============================
async def select_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    indices = [int(x.strip()) - 1 for x in user_input.split(",") if x.strip().isdigit()]

    selected = [MARKETS[i] for i in indices if 0 <= i < len(MARKETS)]

    if not selected:
        await update.message.reply_text("❌ Invalid selection. Try again.")
        return SELECT_MARKET

    context.user_data["markets"] = selected
    await update.message.reply_text("🔢 How many signals do you want?")
    return NUM_SIGNALS

# ==============================
# 🔢 NUMBER OF SIGNALS
# ==============================
async def num_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Enter a valid number.")
        return NUM_SIGNALS

    context.user_data["num_signals"] = int(update.message.text)
    await update.message.reply_text("⏱ Enter total time window (in minutes):")
    return TIME_WINDOW

# ==============================
# ⏱ TIME WINDOW + SIGNAL GEN
# ==============================
async def time_window(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Enter a valid number.")
        return TIME_WINDOW

    total_minutes = int(update.message.text)
    num_signals = context.user_data["num_signals"]
    markets = context.user_data["markets"]

    now = datetime.now(dhaka)
    used_times = set()
    signals = []

    for _ in range(num_signals):
        m = random.choice(markets)

        while True:
            rand_minute = random.randint(5, total_minutes + 5)
            signal_time = now + timedelta(minutes=rand_minute)
            if signal_time not in used_times:
                used_times.add(signal_time)
                break

        direction = random.choice(["UP", "DOWN"])
        confidence = random.randint(85, 95)

        signals.append((signal_time, m, direction, confidence))

    signals.sort(key=lambda x: x[0])

    msg = f"🚀📊 *IIB Future Signals for next {total_minutes} minutes*\n\n"

    for t, m, d, c in signals:
        emoji = "🟢" if d == "UP" else "🔴"
        msg += f"{emoji} *{m}* → `{t.strftime('%I:%M %p')}` : *{d}* | {c}%\n"

    msg += "\n✅ **Signals generated** by **IIB**"

    await update.message.reply_text(msg, parse_mode="Markdown")
    return ConversationHandler.END

# ==============================
# ❌ CANCEL
# ==============================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Operation cancelled.")
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
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),  # 🔥 restart anytime
        ],
        allow_reentry=True
    )

    app.add_handler(conv)
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()




