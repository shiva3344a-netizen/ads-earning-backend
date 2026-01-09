import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("USER_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBAPP_URL = os.getenv("WEBAPP_URL")
BOT_USERNAME = "AdsEarning_43_Bot"

# ================= DATABASE (DEMO) =================
users = {}
withdraw_requests = []
# users[user_id] = {
#   balance: float,
#   refs: int,
# }

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    # referral
    if context.args:
        try:
            ref = int(context.args[0])
            if ref != uid:
                users.setdefault(ref, {"balance": 0.0, "refs": 0})
                users[ref]["refs"] += 1
                users[ref]["balance"] += 0.01
        except:
            pass

    users.setdefault(uid, {"balance": 0.0, "refs": 0})

    keyboard = [
        [InlineKeyboardButton("💰 Open Earn App", url=WEBAPP_URL)],
        [InlineKeyboardButton("📊 Balance", callback_data="balance")],
        [InlineKeyboardButton("👥 Referral", callback_data="referral")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
    ]

    await update.message.reply_text(
        "👋 Welcome!\n\nStart earning by watching ads 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BALANCE =================
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    bal = users.get(uid, {}).get("balance", 0.0)
    await update.message.reply_text(
        f"💰 Balance: ${bal:.4f}\nMin Withdraw: $0.05"
    )

# ================= REFERRAL =================
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    refs = users.get(uid, {}).get("refs", 0)
    link = f"https://t.me/{BOT_USERNAME}?start={uid}"

    await update.message.reply_text(
        f"👥 Referral Program (20% Lifetime)\n\n"
        f"Your Referrals: {refs}\n\n"
        f"🔗 Link:\n{link}"
    )

# ================= WITHDRAW REQUEST =================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    bal = users.get(uid, {}).get("balance", 0.0)

    if bal < 0.05:
        await update.message.reply_text("❌ Minimum withdraw is $0.05")
        return

    await update.message.reply_text(
        "Send withdraw command like this 👇\n\n"
        "`/request USDT_BEP20 YOUR_WALLET_ADDRESS`",
        parse_mode="Markdown"
    )

# ================= REQUEST =================
async def request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if len(context.args) != 2:
        await update.message.reply_text("❌ Format:\n/request USDT_BEP20 WALLET")
        return

    method, wallet = context.args
    if method != "USDT_BEP20":
        await update.message.reply_text("❌ Only USDT BEP20 allowed")
        return

    bal = users.get(uid, {}).get("balance", 0.0)
    if bal < 0.05:
        await update.message.reply_text("❌ Insufficient balance")
        return

    req_id = len(withdraw_requests) + 1
    withdraw_requests.append({
        "id": req_id,
        "user": uid,
        "amount": bal,
        "wallet": wallet
    })

    await update.message.reply_text("✅ Withdraw request sent to admin")

    # notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💸 Withdraw Request #{req_id}\n\n"
            f"User: `{uid}`\n"
            f"Amount: ${bal:.4f}\n"
            f"Wallet: `{wallet}`\n\n"
            f"/approve {req_id}\n"
            f"/reject {req_id}"
        ),
        parse_mode="Markdown"
    )

# ================= ADMIN APPROVE =================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    rid = int(context.args[0])
    req = next((r for r in withdraw_requests if r["id"] == rid), None)
    if not req:
        await update.message.reply_text("❌ Invalid request ID")
        return

    users[req["user"]]["balance"] = 0.0
    withdraw_requests.remove(req)

    await update.message.reply_text(f"✅ Approved request #{rid}")
    await context.bot.send_message(req["user"], "✅ Withdraw approved")

# ================= ADMIN REJECT =================
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    rid = int(context.args[0])
    req = next((r for r in withdraw_requests if r["id"] == rid), None)
    if not req:
        await update.message.reply_text("❌ Invalid request ID")
        return

    withdraw_requests.remove(req)
    await update.message.reply_text(f"❌ Rejected request #{rid}")
    await context.bot.send_message(req["user"], "❌ Withdraw rejected")

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("request", request))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("reject", reject))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
