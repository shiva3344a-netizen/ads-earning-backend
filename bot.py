import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================= CONFIG =================
USER_BOT_TOKEN = os.getenv("USER_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
BOT_USERNAME = "AdsEarning_43_Bot"

# ================= TEMP DATABASE =================
users = {}
# users[user_id] = {
#   "balance": float,
#   "referrals": int,
#   "ref_by": int | None
# }

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

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

        if ref_by and ref_by in users and ref_by != user_id:
            users[ref_by]["referrals"] += 1

    keyboard = [
        [InlineKeyboardButton("💰 Open Earn App", url=WEBAPP_URL)],
        [InlineKeyboardButton("👥 Referral", callback_data="referral")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")]
    ]

    await update.message.reply_text(
        "👋 Welcome!\n\nStart earning by watching ads 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BALANCE =================
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = users.get(user_id, {}).get("balance", 0.0)

    await update.message.reply_text(
        f"💰 Your Balance: ${bal:.4f}\n"
        f"Minimum Withdraw: $0.05"
    )

# ================= REFERRAL (COMMAND) =================
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    refs = users.get(user_id, {}).get("referrals", 0)
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    await update.message.reply_text(
        f"👥 Referral Program\n\n"
        f"Your Referrals: {refs}\n"
        f"Lifetime Commission: 20%\n\n"
        f"🔗 Your Link:\n{ref_link}"
    )

# ================= WITHDRAW (COMMAND) =================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = users.get(user_id, {}).get("balance", 0.0)

    if bal < 0.05:
        await update.message.reply_text("❌ Minimum withdraw is $0.05")
    else:
        await update.message.reply_text(
            "✅ Withdraw request received.\nAdmin will review it."
        )

# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "referral":
        refs = users.get(user_id, {}).get("referrals", 0)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

        await query.message.reply_text(
            f"👥 Referral Program\n\n"
            f"Your Referrals: {refs}\n"
            f"Lifetime Commission: 20%\n\n"
            f"🔗 Your Link:\n{ref_link}"
        )

    elif query.data == "withdraw":
        bal = users.get(user_id, {}).get("balance", 0.0)

        if bal < 0.05:
            await query.message.reply_text("❌ Minimum withdraw is $0.05")
        else:
            await query.message.reply_text(
                "✅ Withdraw request sent.\nAdmin will review it."
            )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(USER_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("withdraw", withdraw))

    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
