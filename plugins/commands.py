import os
import sys
import asyncio 
import datetime
import psutil
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# Import your custom modules
from database import db
from config import Config, temp
from translation import Translation

#===================Global Configurations===================#

START_TIME = datetime.datetime.now()

# Define main menu buttons once to avoid repetition
main_buttons = [
    [
        InlineKeyboardButton("🛡️ sᴛᴀꜰꜰ ᴀᴄᴄᴇss", url="https://t.me/Hayato_ku"),
        InlineKeyboardButton("⚡ ᴄᴏʀᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/DmOwner")
    ],
    [
        InlineKeyboardButton("🛠️ ʜᴇʟᴘ", callback_data="help"),
        InlineKeyboardButton("🛡️ sᴇssɪᴏɴ ɪɴꜰᴏ", callback_data="about")
    ]
]

# Helper for background sticker deletion
async def delete_after_delay(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass

def format_uptime():
    uptime = datetime.datetime.now() - START_TIME
    seconds = int(uptime.total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    
    parts = []
    if days > 0: parts.append(f"{days}D")
    if hours > 0: parts.append(f"{hours}H")
    if minutes > 0: parts.append(f"{minutes}M")
    if seconds > 0: parts.append(f"{seconds}S")
    return ", ".join(parts)

#===================Start Function===================#

@Client.on_message(filters.private & filters.command(['start']))
async def start(client: Client, message: Message):
    user = message.from_user
    
    # 1. Force Subscription Check
    if Config.FORCE_SUB_ON:
        try:
            member = await client.get_chat_member(Config.FORCE_SUB_CHANNEL, user.id)
            if member.status == enums.ChatMemberStatus.BANNED:
                await message.reply_text("<b>You are banned from using this bot.</b>")
                return
        except Exception:
            # If user is not in channel, an exception is raised
            f_sub = str(Config.FORCE_SUB_CHANNEL)
            invite_link = f_sub if "t.me" in f_sub else f"https://t.me/{f_sub.replace('@', '')}"
            
            join_button = [
                [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite_link)],
                [InlineKeyboardButton("↻ ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{client.me.username}?start=start")]
            ]
            await message.reply_text(
                text="<b>ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.</b>",
                reply_markup=InlineKeyboardMarkup(join_button)
            )
            return

    # 2. Database & Logging Logic
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        # Log to private channel
        await client.send_message(
            chat_id=Config.LOG_CHANNEL,
            text=f"#NewUser\n\n<b>ID:</b> <code>{user.id}</code>\n<b>Name:</b> {user.mention}"
        )

    # 3. Sticker Logic (Non-blocking)
    try:
        sticker_msg = await message.reply_sticker("CAACAgUAAxkBAAEQLstpXRZxNxFMteYSkppBZ63fuBhVtQACFBgAAtDQQVbGUaezY8jttzgE")
        asyncio.create_task(delete_after_delay(sticker_msg, 2))
    except Exception:
        pass

    # 4. Final Welcome Message
    await message.reply_text(
        text=Translation.START_TXT.format(user.first_name),
        reply_markup=InlineKeyboardMarkup(main_buttons),
        quote=True
    )

#==================Restart Function==================#

@Client.on_message(filters.private & filters.command(['restart']) & filters.user(Config.BOT_OWNER_ID))
async def restart_bot(client: Client, message: Message):
    msg = await message.reply_text("<i>ᴛʀʏɪɴɢ ᴛᴏ ʀᴇsᴛᴀʀᴛ sᴇʀᴠᴇʀ...</i>")
    await asyncio.sleep(2)
    await msg.edit("<i>sᴇʀᴠᴇʀ ʀᴇsᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✅</i>")
    os.execl(sys.executable, sys.executable, *sys.argv)

#==================Callback Functions==================#

@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    data = query.data
    
    if data == "back":
        await query.message.edit_text(
            text=Translation.START_TXT.format(query.from_user.first_name),
            reply_markup=InlineKeyboardMarkup(main_buttons)
        )
        
    elif data == "help":
        buttons = [
            [InlineKeyboardButton('• ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ ❓', callback_data='how_to_use')],
            [InlineKeyboardButton('• sᴇᴛᴛɪɴɢs ', callback_data='settings#main'),
             InlineKeyboardButton('• sᴛᴀᴛᴜs ', callback_data='status')],
            [InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='back'),
             InlineKeyboardButton('• ᴀʙᴏᴜᴛ', callback_data='about')]
        ]
        await query.message.edit_text(
            text=Translation.HELP_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    elif data == "how_to_use":
        await query.message.edit_text(
            text=Translation.HOW_USE_TXT,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='help')]]),
            disable_web_page_preview=True
        )

    elif data == "about":
        await query.message.edit_text(
            text=Translation.ABOUT_TXT,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='back')]]),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "status":
        users_count, bots_count = await db.total_users_bots_count()
        total_channels = await db.total_channels()
        uptime_str = format_uptime()
        
        await query.message.edit_text(
            text=Translation.STATUS_TXT.format(users_count, bots_count, temp.forwardings, total_channels, uptime_str),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='help'),
                 InlineKeyboardButton('• sᴇʀᴠᴇʀ sᴛᴀᴛs', callback_data='server_status')]
            ]),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

    elif data == "server_status":
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent()
        await query.message.edit_text(
            text=Translation.SERVER_TXT.format(cpu, ram),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='status')]]),
            parse_mode=enums.ParseMode.HTML
        )

#===================Donate Function===================#

@Client.on_message(filters.private & filters.command(['donate']))
async def donate_cmd(client: Client, message: Message):
    await message.reply_text(
        text="<i>__If you liked my service❤__.\n\nConsider and make a donation to support my developer 👦\n\n\n ID - `@DmOwner`</i>"
    )
