import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================
USER_BOT_TOKEN = os.getenv("USER_BOT_TOKEN")

WEBAPP_URL = "https://telegram-earn-app.vercel.app"
BOT_USERNAME = "AdsEarning_43_Bot"

# ================= TEMP DATABASE =================
users = {}  
# users[user_id] = {
#   "balance": float,
#   "referrals": int,
#   "ref_by": user_id or None
# }

# ================= START COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # referral handling
    ref_by = None
    if context.args:
        try:
            ref_by = int(context.args[0])
        except:
            ref_by = None

    if user_id not in users:
        users[user_id] = {
            "balance": 0.0,
            "referrals": 0,
            "ref_by": ref_by
        }

        if ref_by and ref_by in users:
            users[ref_by]["referrals"] += 1

    keyboard = [
        [InlineKeyboardButton("💰 Open Earn App", url=WEBAPP_URL)],
        [InlineKeyboardButton("👥 Referral", callback_data="referral")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome!\n\nStart earning by watching ads 👇",
        reply_markup=reply_markup
    )

# ================= BALANCE =================
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = users.get(user_id, {}).get("balance", 0.0)

    await update.message.reply_text(
        f"💰 Your Balance: ${bal:.4f}\n\n"
        f"Minimum Withdraw: $0.05"
    )

# ================= REFERRAL =================
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    refs = users.get(user_id, {}).get("referrals", 0)

    await update.message.reply_text(
        f"👥 Referral Program\n\n"
        f"Your Referrals: {refs}\n"
        f"Lifetime Commission: 20%\n\n"
        f"🔗 Your Link:\n{ref_link}"
    )

# ================= WITHDRAW =================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = users.get(user_id, {}).get("balance", 0.0)

    if bal < 0.05:
        await update.message.reply_text(
            "❌ Minimum withdraw is $0.05"
        )
    else:
        await update.message.reply_text(
            "✅ Withdraw request received.\nAdmin will review it."
        )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(USER_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("withdraw", withdraw))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
