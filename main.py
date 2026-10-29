import asyncio
import html
import json
import os
import random
import time
from datetime import datetime
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode
from telegram.error import RetryAfter, TimedOut, NetworkError, BadRequest

# ===================== RAID MESSAGES IMPORT =====================
from raid_messages import RAID_MESSAGES


# =====================================================================
# 🔥🔥🔥 YAHAN APNE 10 BOT TOKENS PASTE KARO 🔥🔥🔥
# =====================================================================
# Har line me ek token. Jo bot nahi chahiye uski line ko khaali chhod do ""
# Example: BOT_TOKEN3 = ""  -> woh bot nahi chalega.

BOT_TOKEN1  = "9246982060:AAEeUsxi9pdmZXArRT5YBIfBxfvZEviCLOI"
BOT_TOKEN2  = "8609648734:AAG_kv-lREhqnUxFL8f-dcHYMDe3wASr46E"
BOT_TOKEN3  = "8753354699:AAEWhyWQ2IMFvJJ0DQj1Zw1R4IeH0dc_sP0"
BOT_TOKEN4  = "8701467251:AAFG45zT8JsFppTikmJGuI-BN8fr6PSocLw"
BOT_TOKEN5  = "8808041749:AAEfOHFazDocB0S_WQ0x5WFmTxK1IPVkJZg"
BOT_TOKEN6  = "8813725599:AAEXkPfpRpHAvgcyKIBwp9HiGp178XmvRis"
BOT_TOKEN7  = "8766060881:AAEzvOvsGUROUx9JQirjVh9kVxnWy4O5r1Q"
BOT_TOKEN8  = "8870176881:AAEcnxkdGWU9zJog7FHF3VaRinDMVXJmJqc"
BOT_TOKEN9  = "8422933963:AAH37p_zfR8yqu1fjvOZNQSASdjDROLHxyM"
BOT_TOKEN10 = "9127368681:AAEUgIfnvH5QNWL57qMt3qLuQ19JCb4JGk0"

# =====================================================================
# Baaki kuch change mat karo niche
# =====================================================================


# ===================== RENDER DUMMY SERVER =====================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "💀 Sasuke Destruction Bot is Alive! 💀"

def run_web():
    try:
        port = int(os.environ.get("PORT", 8080))
        web_app.run(host="0.0.0.0", port=port, use_reloader=False)
    except Exception:
        pass

# ===================== VIP CONFIGURATION =====================
API_ID = int(os.getenv("API_ID", 39782277))
API_HASH = os.getenv("API_HASH", "c17770cb00d3f63a83ff58028e80cbd4")

# Tokens ko list me convert karo (jo khaali hain unhe skip karo)
BOT_TOKENS = [
    BOT_TOKEN1, BOT_TOKEN2, BOT_TOKEN3, BOT_TOKEN4, BOT_TOKEN5,
    BOT_TOKEN6, BOT_TOKEN7, BOT_TOKEN8, BOT_TOKEN9, BOT_TOKEN10
]
BOT_TOKENS = [t.strip() for t in BOT_TOKENS if t and t.strip()]

if not BOT_TOKENS:
    raise RuntimeError("❌ Koi bhi BOT_TOKEN nahi mila! Upar BOT_TOKEN1 se BOT_TOKEN10 me tokens paste karo.")

owner_string = os.getenv("OWNER_ID", "8672927645 8882297263")
OWNER_ID = [int(i) for i in owner_string.replace(',', ' ').split() if i.strip().isdigit()]

# ===================== STABLE SPEED SETTING =====================
MESSAGE_DELAY = 0.2
CURRENT_MODE = "MEDIUM"
BATCH_SIZE = 5
MAX_RETRIES = 999999

# ===================== DATABASE FILES =====================
SUDO_USERS_FILE = 'sudo_users.json'
BOT_DATA_FILE = 'bot_data.json'
STICKERS_FILE = 'saved_stickers.json'

# ===================== GLOBALS =====================
sudo_users = {}
active_operations = {}
saved_stickers = []
start_time = time.time()

# Multi-quote welcome UI
WELCOME_TEXT = """<blockquote>🐉🦫 <b>ꜱᴜꜱᴀᴋᴇ ᴅᴇꜱᴛʀᴜᴄᴛɪᴏɴ ʙᴏᴛ</b> 🐉🦫</blockquote>
<blockquote><b>ꜱᴢᴢᴮᴛ ᴀᴄᴄᴏᴜɴᴛꜱ...</b>
<b>ꜱᴢᴢᴮᴛ ᴀᴄᴄᴏᴜɴᴛꜱ ᴀʟʟ ᴍᴏᴅᴇ...</b>
<b>ᴘᴏᴡᴇʀ ᴍᴏᴅᴇ: ᴀᴄᴛɪᴠᴇ</b>
<b>ꜱᴘᴀᴍ ᴍᴏᴅᴇ: ʀᴇᴀᴅʏ</b></blockquote>
<blockquote><b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ꜱᴜꜱᴀᴋᴇ ꜱᴘᴀᴍ ʙᴏᴛ</b> 🐉🦫</blockquote>
<blockquote><b>ʀᴇᴀᴅʏ ᴛᴏ ᴡᴏʀᴋ</b> 🐉🦫</blockquote>"""

BOT_DATA = {
    "photo": ""
}

# ===================== HELP MENU =====================
HELP_TEXT = """<blockquote><b>SASUKE DESTRUCTION BOT - MENU 💀</b>

════════════════════════
🔥 <b>RAID & SPAM COMMANDS</b>
════════════════════════
<code>.raid [count]</code> - Raid (Reply to user)
<code>.spam [count] [text]</code> - Custom Spam (Reply)
📌 Target ko mention aur reply karega!

════════════════════════
🏷 <b>STICKER COMMANDS</b>
════════════════════════
<code>.sticker [count]</code> - Spam stickers (Reply)
<code>.addsticker</code> - Save a sticker (Reply)
<code>.removesticker</code> - Delete sticker (Reply)
<code>.liststickers</code> - Show saved stickers

════════════════════════
⚡ <b>SPEED MODES (OWNER ONLY)</b>
════════════════════════
<code>.mode</code> - Current speed status
<code>.mode [slow/medium/fast]</code> - Change speed

════════════════════════
🔇 <b>ADMIN COMMANDS</b>
════════════════════════
<code>.mute</code> - Mute target (Reply)
<code>.unmute</code> - Unmute target (Reply)

════════════════════════
⚙️ <b>SYSTEM & UTILS</b>
════════════════════════
<code>.alive</code> - Check bot status
<code>.ping</code> - Check Bot Latency & Mode
<code>.help</code> - Show this menu
<code>.stop</code> - Force stop active attacks

💀 <b>SASUKE DESTRUCTION BOT</b> 💀</blockquote>"""

# ===================== DATABASE HANDLING =====================
def load_data():
    global sudo_users, saved_stickers, BOT_DATA
    try:
        if os.path.exists(SUDO_USERS_FILE):
            with open(SUDO_USERS_FILE, 'r') as f: sudo_users = json.load(f)
        if os.path.exists(STICKERS_FILE):
            with open(STICKERS_FILE, 'r') as f: saved_stickers = json.load(f)
        if os.path.exists(BOT_DATA_FILE):
            with open(BOT_DATA_FILE, 'r') as f: BOT_DATA = json.load(f)
    except Exception as e: print(f"❌ Load error: {e}")

def save_data():
    try:
        with open(SUDO_USERS_FILE, 'w') as f: json.dump(sudo_users, f, indent=2)
        with open(STICKERS_FILE, 'w') as f: json.dump(saved_stickers, f, indent=2)
        with open(BOT_DATA_FILE, 'w') as f: json.dump(BOT_DATA, f, indent=2)
    except Exception as e: print(f"❌ Save error: {e}")

load_data()

def is_sudo(user_id: int) -> bool:
    return str(user_id) in sudo_users or user_id in OWNER_ID

def is_owner(user_id: int) -> bool:
    return user_id in OWNER_ID

# ===================== FLOOD PROTECTION ENGINE =====================
async def send_single_msg(context, chat_id, message, reply_to, retry_count=0):
    try:
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_to_message_id=reply_to)
        return True
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 0.5)
        return await send_single_msg(context, chat_id, message, reply_to, retry_count + 1)
    except (TimedOut, NetworkError):
        await asyncio.sleep(1)
        if retry_count < MAX_RETRIES:
            return await send_single_msg(context, chat_id, message, reply_to, retry_count + 1)
        return False
    except Exception:
        return False

async def send_single_sticker(context, chat_id, sticker_id, reply_to, retry_count=0):
    try:
        await context.bot.send_sticker(chat_id=chat_id, sticker=sticker_id, reply_to_message_id=reply_to)
        return True
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 0.5)
        return await send_single_sticker(context, chat_id, sticker_id, reply_to, retry_count + 1)
    except (TimedOut, NetworkError):
        await asyncio.sleep(1)
        if retry_count < MAX_RETRIES:
            return await send_single_sticker(context, chat_id, sticker_id, reply_to, retry_count + 1)
        return False
    except Exception:
        return False

# ===================== UI KEYBOARDS =====================
def get_main_keyboard(bot_username: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴅᴇᴠɪʟ 🛠️", callback_data="show_help"),
            InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ 💬", url="https://t.me/ll_ABOUT_SASUKE_ll")
        ],
        [
            InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ɢʀᴏᴜᴘ ✨", url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_to_main")]
    ])

# ===================== UI & MENU =====================
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bot_info = await context.bot.get_me()
    reply_markup = get_main_keyboard(bot_info.username)

    if update.callback_query:
        query = update.callback_query
        try:
            if query.message.photo:
                await query.edit_message_caption(caption=WELCOME_TEXT, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await query.edit_message_text(text=WELCOME_TEXT, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        except Exception:
            try:
                await query.message.delete()
            except Exception:
                pass
            if BOT_DATA.get('photo'):
                await context.bot.send_photo(chat_id=chat_id, photo=BOT_DATA['photo'], caption=WELCOME_TEXT, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await context.bot.send_message(chat_id=chat_id, text=WELCOME_TEXT, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        if BOT_DATA.get('photo'):
            await context.bot.send_photo(chat_id=chat_id, photo=BOT_DATA['photo'], caption=WELCOME_TEXT, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await context.bot.send_message(chat_id=chat_id, text=WELCOME_TEXT, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'show_help':
        back_btn = get_back_keyboard()
        chat_id = query.message.chat_id

        try:
            if query.message.photo:
                await query.edit_message_caption(caption=HELP_TEXT, reply_markup=back_btn, parse_mode=ParseMode.HTML)
            else:
                await query.edit_message_text(text=HELP_TEXT, reply_markup=back_btn, parse_mode=ParseMode.HTML)
        except Exception:
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(chat_id=chat_id, text=HELP_TEXT, reply_markup=back_btn, parse_mode=ParseMode.HTML)

    elif query.data == 'back_to_main':
        await show_menu(update, context)

# ===================== MASTER COMMAND HANDLER =====================
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MESSAGE_DELAY, CURRENT_MODE
    if not update.message or not update.message.text: return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if not text.startswith('.'): return

    parts = text.split()
    command = parts[0][1:].lower()

    # ------------------ PUBLIC COMMANDS ------------------
    if command == 'ping':
        latency = (time.time() - update.message.date.timestamp()) * 1000
        await update.message.reply_text(f"ᴘᴏɴɢ: {abs(latency):.2f}ᴍꜱ | Mode: {CURRENT_MODE}")
        return

    elif command == 'alive':
        await update.message.reply_text("SASUKE X SPAM AAGYA BATAO KISKO CHODNA HAI")
        return

    elif command == 'help':
        await update.message.reply_text(HELP_TEXT, reply_markup=get_back_keyboard(), parse_mode=ParseMode.HTML)
        return

    # ------------------ SPEED MODES (OWNER ONLY) ------------------
    if command == 'mode':
        if not is_owner(user_id):
            return await update.message.reply_text("⚡ <b>Sirf Owner speed mode check ya change kar sakta hai!</b>", parse_mode=ParseMode.HTML)

        if len(parts) == 1:
            return await update.message.reply_text(
                f"⚡ <b>Current Mode:</b> <code>{CURRENT_MODE}</code>\nDelay: {MESSAGE_DELAY}s\n\nOptions: <code>.mode slow</code> | <code>.mode medium</code> | <code>.mode fast</code>",
                parse_mode=ParseMode.HTML
            )

        mode_choice = parts[1].lower()
        if mode_choice == 'slow':
            MESSAGE_DELAY = 1.0
            CURRENT_MODE = "SLOW"
            await update.message.reply_text("🐢 <b>Speed Mode set to SLOW (1.0s delay)</b>", parse_mode=ParseMode.HTML)
        elif mode_choice == 'medium':
            MESSAGE_DELAY = 0.5
            CURRENT_MODE = "MEDIUM"
            await update.message.reply_text("⚖️ <b>Speed Mode set to MEDIUM (0.5s delay)</b>", parse_mode=ParseMode.HTML)
        elif mode_choice == 'fast':
            MESSAGE_DELAY = 0.1
            CURRENT_MODE = "FAST"
            await update.message.reply_text("🚀 <b>Speed Mode set to FAST (0.1s delay)</b>", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ Invalid mode! Use: <code>slow</code>, <code>medium</code>, ya <code>fast</code>", parse_mode=ParseMode.HTML)
        return

    # ------------------ SUDO & OWNER PROTECTION CHECK ------------------
    if not is_sudo(user_id):
        await update.message.reply_text(
            "PHALE SASUKE SE SUDO LEKE AAO",
            reply_to_message_id=update.message.message_id
        )
        return

    # ------------------ PHOTO CUSTOMIZATION (OWNER ONLY) ------------------
    if command == 'setphoto' and is_owner(user_id):
        if not update.message.reply_to_message or not update.message.reply_to_message.photo:
            return await update.message.reply_text("📌 Photo par reply karke `.setphoto` likh!")
        BOT_DATA['photo'] = update.message.reply_to_message.photo[-1].file_id
        save_data()
        await update.message.reply_text("✅ <b>Banner Photo Updated!</b>", parse_mode=ParseMode.HTML)

    # ------------------ ADMIN COMMANDS (MUTE/UNMUTE) ------------------
    elif command in ['mute', 'unmute']:
        if not update.message.reply_to_message:
            return await update.message.reply_text("📌 Kisi user ko reply karo!")

        target = update.message.reply_to_message.from_user
        can_send = (command == 'unmute')
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat_id, user_id=target.id,
                permissions=ChatPermissions(
                    can_send_messages=can_send, can_send_media_messages=can_send,
                    can_send_other_messages=can_send, can_add_web_page_previews=can_send
                )
            )
            action = "🔊 UNMUTED" if can_send else "🔇 MUTED"
            await update.message.reply_text(f"✅ {action}: {html.escape(target.first_name)}", parse_mode=ParseMode.HTML)
        except Exception:
            await update.message.reply_text("❌ Failed. Bot must be an admin.")

    # ------------------ SUDO SYSTEM (OWNER ONLY) ------------------
    elif command in ['addsudo', 'removesudo'] and is_owner(user_id):
        target_id, target_name = None, "User"
        if update.message.reply_to_message:
            target_id = update.message.reply_to_message.from_user.id
            target_name = update.message.reply_to_message.from_user.first_name
        elif len(parts) >= 2 and parts[1].lstrip('-').isdigit():
            target_id = int(parts[1])
            target_name = f"User_{target_id}"

        if not target_id: return await update.message.reply_text(f"📌 Usage: `.{command} [ID]` ya message pe reply kar.")

        if command == 'addsudo':
            if str(target_id) in sudo_users: return await update.message.reply_text("⚡ Ye user pehle se Sudo hai!")
            sudo_users[str(target_id)] = {'name': target_name, 'added': datetime.now().isoformat()}
            save_data()
            await update.message.reply_text(f"✅ <b>SUDO ADDED!</b>\nUser: {html.escape(target_name)}\nID: <code>{target_id}</code>", parse_mode=ParseMode.HTML)
        else:
            if target_id in OWNER_ID: return await update.message.reply_text("❌ Owner ko remove nahi kar sakte!")
            if str(target_id) not in sudo_users: return await update.message.reply_text("❌ Ye user Sudo list me nahi hai!")
            del sudo_users[str(target_id)]
            save_data()
            await update.message.reply_text(f"🗑 <b>SUDO REMOVED:</b> {html.escape(target_name)}", parse_mode=ParseMode.HTML)

    elif command == 'listsudo' and is_owner(user_id):
        if not sudo_users: return await update.message.reply_text("📭 No Sudo Users!")
        msg = "👑 <b>AUTHORIZED SUDO USERS</b> 👑\n\n"
        for uid, info in sudo_users.items(): msg += f"⚡ <b>{html.escape(info['name'])}</b> (<code>{uid}</code>)\n"
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

    # ------------------ STICKER SYSTEM ------------------
    elif command == 'addsticker' and is_owner(user_id):
        if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
            return await update.message.reply_text("📌 Sticker par reply karke `.addsticker` likh!")
        stk_id = update.message.reply_to_message.sticker.file_id
        if stk_id not in saved_stickers:
            saved_stickers.append(stk_id)
            save_data()
            await update.message.reply_text(f"✅ <b>Sticker Saved!</b> (Total: {len(saved_stickers)})", parse_mode=ParseMode.HTML)
        else: await update.message.reply_text("⚡ Already saved!")

    elif command == 'removesticker' and is_owner(user_id):
        if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
            return await update.message.reply_text("📌 Sticker par reply karke `.removesticker` likh!")
        stk_id = update.message.reply_to_message.sticker.file_id
        if stk_id in saved_stickers:
            saved_stickers.remove(stk_id)
            save_data()
            await update.message.reply_text("🗑 <b>Sticker Removed!</b>", parse_mode=ParseMode.HTML)

    elif command == 'liststickers':
        await update.message.reply_text(f"⚡ Total Saved Stickers: {len(saved_stickers)}")

    # ------------------ SYSTEM UTILS ------------------
    elif command == 'stop':
        active_operations.pop(str(chat_id), None)
        await update.message.reply_text("🛑 <b>ALL DESTRUCTION PROTOCOLS STOPPED!</b>", parse_mode=ParseMode.HTML)

    # ------------------ ATTACK / SEND ENGINE ------------------
    elif command in ['spam', 'raid', 'sticker']:
        if len(parts) < 2 or not parts[1].isdigit():
            return await update.message.reply_text(f"📌 <b>Galat format!</b> Usage: <code>.{command} [count]</code> likh kar reply karo.", parse_mode=ParseMode.HTML)

        if not update.message.reply_to_message:
            return await update.message.reply_text(f"📌 Jisko target karna hai uske message par reply karke <code>.{command} [count]</code> likho!", parse_mode=ParseMode.HTML)

        target = update.message.reply_to_message.from_user

        # 🛡️ OWNER PROTECTION
        if target.id in OWNER_ID:
            return await update.message.reply_text("⚡ <b>AUKAT ME REH BHAI OWNER PE KAREGA TMKC!</b> 👑", parse_mode=ParseMode.HTML)

        target_msg_id = update.message.reply_to_message.message_id
        count = int(parts[1])

        if command == 'sticker' and not saved_stickers:
            return await update.message.reply_text("KOI STICKER TO KAR PHALE GARIB")

        spam_text = "CHUD GYA BSDKA GARIB"
        if command == 'spam' and len(parts) > 2:
            spam_text = " ".join(parts[2:])

        active_operations[str(chat_id)] = True
        await update.message.reply_text(f"⚡ <b>{command.upper()} INITIATED ON {html.escape(target.first_name)}</b> (x{count}) | Mode: {CURRENT_MODE}", parse_mode=ParseMode.HTML)

        async def destruction_task():
            sent = 0
            while sent < count and active_operations.get(str(chat_id)):
                batch = min(BATCH_SIZE, count - sent)
                tasks = []

                for _ in range(batch):
                    if command == 'sticker':
                        stk_id = random.choice(saved_stickers)
              
