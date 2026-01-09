import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

USER_BOT_TOKEN = os.getenv("USER_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

users = {}  # simple in-memory db

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # referral handling
    if context.args:
        referrer = int(context.args[0])
        if referrer != user_id:
            users.setdefault(referrer, {"balance": 0, "refs": 0})
            users[referrer]["refs"] += 1
            users[referrer]["balance"] += 0.01  # referral bonus

    users.setdefault(user_id, {"balance": 0, "refs": 0})

    keyboard = [
        [InlineKeyboardButton("💰 Open Earn App", url=WEBAPP_URL)],
        [InlineKeyboardButton("👥 Referral", callback_data="referral")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")]
    ]

    await update.message.reply_text(
        "👋 Welcome!\nStart earning by watching ads 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- BALANCE ----------
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = users.get(user_id, {}).get("balance", 0)
    await update.message.reply_text(f"💰 Your Balance: ${bal:.4f}")

# ---------- REFERRAL ----------
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    refs = users.get(user_id, {}).get("refs", 0)
    ref_link = f"https://t.me/AdsEarning_43_Bot?start={user_id}"

    await update.message.reply_text(
        f"👥 Referral Program\n\n"
        f"Your Referrals: {refs}\n"
        f"Lifetime Commission: 20%\n\n"
        f"🔗 Your Link:\n{ref_link}"
    )

# ---------- WITHDRAW ----------
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = users.get(user_id, {}).get("balance", 0)

    if bal < 0.05:
        await update.message.reply_text("❌ Minimum withdraw is $0.05")
    else:
        await update.message.reply_text(
            "✅ Withdraw request received.\nAdmin will process it manually."
        )

# ---------- MAIN ----------
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
