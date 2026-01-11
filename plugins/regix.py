import os
import sys 
import math
import time
import asyncio 
import logging
import random
from .utils import STS
from database import db 
from .test import CLIENT , start_clone_bot
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.errors import FloodWait, MessageNotModified, RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 

CLIENT = CLIENT()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEXT = Translation.TEXT

#===================Public Start Function===================#

@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user = message.from_user.id
    temp.CANCEL[user] = False
    frwd_id = message.data.split("_")[2]
    
    if temp.lock.get(user) and str(temp.lock.get(user)) == "True":
        return await message.answer("ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟʟ ᴘʀᴇᴠɪᴏᴜs ᴛᴀsᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.", show_alert=True)
    
    sts = STS(frwd_id)
    if not sts.verify():
        await message.answer("ʏᴏᴜ ᴀʀᴇ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ᴍʏ ᴏɴᴇ ᴏғ ᴏʟᴅ ʙᴜᴛᴛᴏɴ.", show_alert=True)
        return await message.message.delete()
    
    i = sts.get(full=True)
    if i.TO in temp.IS_FRWD_CHAT:
        return await message.answer("ɪɴ ᴛᴀʀɢᴇᴛ ᴄʜᴀᴛ ᴛᴀsᴋ ɪs ɪɴ ᴘʀᴏɢʀᴇss.", show_alert=True)
    
    m = await msg_edit(message.message, "<i><b>vᴇʀɪғʏɪɴɢ ʏᴏᴜʀ ᴅᴀᴛᴀ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b></i>")
    _bot, caption, forward_tag, data, protect, button = await sts.get_data(user)
    
    if not _bot:
        return await msg_edit(m, "<code>ʏᴏᴜ ᴅɪᴅ ɴᴏᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ʙᴏᴛ ʏᴇᴛ ᴜsᴇ /settings</code>", wait=True)
    
    try:
        client = await start_clone_bot(CLIENT.client(_bot))
    except Exception as e:    
        return await m.edit(f"**Error:** {e}")
    
    await msg_edit(m, "<b>ᴘʀᴏᴄᴇssɪɴɢ..</b>")
    try: 
        await client.get_messages(sts.get("FROM"), 1)
    except:
        await msg_edit(m, f"**sᴏᴜʀᴄᴇ ᴄʜᴀᴛ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ.**", retry_btn(frwd_id), True)
        return await stop(client, user)

    temp.forwardings += 1
    await db.add_frwd(user)
    await send(client, user, "<b>🚥 100ᴋ+ sᴀғᴇ-ᴍᴏᴅᴇ ғᴏʀᴡᴀʀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ</b>")
    sts.add(time=True)

    # === SAFETY CONFIGURATION ===
    is_bot = _bot['is_bot']
    # Human-mimicry delays
    base_sleep = 2.0 if is_bot else 4.5 
    batch_sleep = 8.0 if is_bot else 25.0
    
    # Milestone Tracking for the 10k Pause
    milestone_limit = 10000
    milestone_counter = 0 
    
    await msg_edit(m, "<code>ᴘʀᴏᴄᴇssɪɴɢ ...</code>")
    temp.IS_FRWD_CHAT.append(i.TO)
    temp.lock[user] = True
    
    try:
        MSG = []
        last_edit_time = time.time()
        
        async for message in client.iter_messages(
            chat_id=sts.get('FROM'),
            limit=int(sts.get('limit')),
            offset=int(sts.get('skip')) if sts.get('skip') else 0
        ):
            if await is_cancelled(client, user, m, sts):
                return

            # Milestone Check: Every 10,000 files, sleep for 15 minutes
            if milestone_counter >= milestone_limit:
                await edit(m, 'ᴅᴇᴇᴘ sʟᴇᴇᴘ (15ᴍ)', 900, sts)
                await asyncio.sleep(900) 
                milestone_counter = 0 # Reset counter
                last_edit_time = time.time() # Reset UI timer

            # Update UI every 60 seconds (Safe for massive tasks)
            if time.time() - last_edit_time > 60:
                await edit(m, 'ᴘʀᴏɢʀᴇssɪɴɢ', 10, sts)
                last_edit_time = time.time()

            sts.add('fetched')
            if message.empty or message.service:
                sts.add('deleted')
                continue
            
            # Use forward_tag logic with randomized batching
            if forward_tag:
                MSG.append(message.id)
                random_batch = random.randint(35, 75) # Randomized batch size
                
                if len(MSG) >= random_batch:
                    await forward(client, MSG, m, sts, protect)
                    sts.add('total_files', len(MSG))
                    milestone_counter += len(MSG)
                    MSG = []
                    # Jitter sleep after batch
                    await asyncio.sleep(batch_sleep + random.uniform(1.0, 5.0))
            else:
                new_caption = custom_caption(message, caption)
                details = {"msg_id": message.id, "media": media(message), "caption": new_caption, 'button': button, "protect": protect}
                await copy(client, details, m, sts)
                sts.add('total_files')
                milestone_counter += 1
                # Human-like randomized delay per file
                await asyncio.sleep(base_sleep + random.uniform(0.5, 2.5))
                
        # Final cleanup for remaining messages in list
        if MSG:
            await forward(client, MSG, m, sts, protect)
            sts.add('total_files', len(MSG))

    except Exception as e:
        logger.error(f"Forwarding Critical Error: {e}")
        await msg_edit(m, f'<b>ERROR:</b>\n<code>{e}</code>', wait=True)
    
    temp.IS_FRWD_CHAT.remove(i.TO)
    await send(client, user, "<b>🎉 ᴍᴀss ғᴏʀᴡᴀʀᴅɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>")
    await edit(m, 'ᴄᴏᴍᴘʟᴇᴛᴇᴅ', "ᴄᴏᴍᴘʟᴇᴛᴇᴅ", sts) 
    await stop(client, user)

# --- PROTECTED NETWORK WRAPPERS ---

async def copy(bot, msg, m, sts):
    try:                                  
        if msg.get("media") and msg.get("caption"):
            await bot.send_cached_media(
                chat_id=sts.get('TO'),
                file_id=msg.get("media"),
                caption=msg.get("caption"),
                reply_markup=msg.get('button'),
                protect_content=msg.get("protect"))
        else:
            await bot.copy_message(
                chat_id=sts.get('TO'),
                from_chat_id=sts.get('FROM'),    
                caption=msg.get("caption"),
                message_id=msg.get("msg_id"),
                reply_markup=msg.get('button'),
                protect_content=msg.get("protect"))
    except FloodWait as e:
        # Extreme Safety: Add 30 seconds to whatever Telegram asks
        wait_time = e.value + 30
        await edit(m, 'sʟᴇᴇᴘɪɴɢ', wait_time, sts)
        await asyncio.sleep(wait_time)
        await copy(bot, msg, m, sts)
    except Exception:
        sts.add('deleted')

async def forward(bot, msg_ids, m, sts, protect):
    try:                             
        await bot.forward_messages(
            chat_id=sts.get('TO'),
            from_chat_id=sts.get('FROM'), 
            protect_content=protect,
            message_ids=msg_ids)
    except FloodWait as e:
        wait_time = e.value + 40
        await edit(m, 'sʟᴇᴇᴘɪɴɢ', wait_time, sts)
        await asyncio.sleep(wait_time)
        await forward(bot, msg_ids, m, sts, protect)

# --- UI & FORMATTING ---

async def edit(msg, title, status, sts):
    try:
        i = sts.get(full=True)
        status_text = 'sᴀғᴇ-ғᴏʀᴡᴀʀᴅɪɴɢ' if status == 10 else f"sʟᴇᴇᴘɪɴɢ {status} s" if str(status).isnumeric() else status
        
        total = i.total if i.total > 0 else 1
        percentage = "{:.1f}".format(float(i.fetched)*100/float(total))
        
        p_val = math.floor(float(percentage) / 10)
        bar = "▰" * p_val + "▱" * (10 - p_val)
        
        text = TEXT.format(i.total, i.fetched, i.total_files, i.duplicate, i.deleted, i.skip, i.filtered, status_text, percentage, title)
        
        kb = [[InlineKeyboardButton(f"{bar} {percentage}%", "status_info")]]
        if status in ["ᴄᴀɴᴄᴇʟʟᴇᴅ", "ᴄᴏᴍᴘʟᴇᴛᴇᴅ"]:
            kb.append([InlineKeyboardButton('🗑️ ᴄʟᴏsᴇ', 'close_btn')])
        else:
            kb.append([InlineKeyboardButton('🛑 sᴛᴏᴘ ᴘʀᴏᴄᴇss', 'terminate_frwd')])
            
        await msg_edit(msg, text, InlineKeyboardMarkup(kb))
    except:
        pass

async def is_cancelled(client, user, msg, sts):
    if temp.CANCEL.get(user):
        temp.IS_FRWD_CHAT.remove(sts.TO)
        await edit(msg, "ᴄᴀɴᴄᴇʟʟᴇᴅ", "ᴄᴏᴍᴘʟᴇᴛᴇᴅ", sts)
        await stop(client, user)
        return True 
    return False 

async def stop(client, user):
    try: await client.stop()
    except: pass 
    await db.rmve_frwd(user)
    temp.forwardings = max(0, temp.forwardings - 1)
    temp.lock[user] = False 

def custom_caption(msg, caption):
    if msg.media:
        media_obj = getattr(msg, msg.media.value, None)
        if media_obj:
            fcap = getattr(msg, 'caption', '')
            if fcap: fcap = fcap.html
            if caption:
                return caption.format(filename=getattr(media_obj, 'file_name', ''), 
                                    size=get_size(getattr(media_obj, 'file_size', 0)), 
                                    caption=fcap)
            return fcap
    return None

def get_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0: return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def media(msg):
    if msg.media:
        media_obj = getattr(msg, msg.media.value, None)
        if media_obj: return getattr(media_obj, 'file_id', None)
    return None 

async def msg_edit(msg, text, button=None, wait=None):
    try: return await msg.edit(text, reply_markup=button)
    except MessageNotModified: pass 
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await msg_edit(msg, text, button, wait)

async def send(bot, user, text):
    try: await bot.send_message(user, text=text)
    except: pass 

def retry_btn(id):
    return InlineKeyboardMarkup([[InlineKeyboardButton('♻️ ʀᴇᴛʀʏ ♻️', f"start_public_{id}")]])

@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, m):
    temp.CANCEL[m.from_user.id] = True 
    await m.answer("🛑 ʜᴀʟᴛɪɴɢ ᴘʀᴏᴄᴇss...", show_alert=True)

@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.message.delete()
