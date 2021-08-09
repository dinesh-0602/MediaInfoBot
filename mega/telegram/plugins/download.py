import os
import re
import secrets
import asyncio
import logging
import tldextract
import humanfriendly as size
from mega.common import Common
from pyrogram import emoji, Client
from mega.helpers.ytdl import YTdl
from mega.helpers.screens import Screens
#from mega.database.files import MegaFiles
#from mega.database.users import MegaUsers
#from mega.helpers.seerd_api import SeedrAPI
from pyrogram.errors import MessageNotModified
from mega.helpers.media_info import MediaInfo
from mega.helpers.uploader import UploadFiles
from mega.helpers.downloader import Downloader
from mega.telegram.utils.custom_download import TGCustomYield
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ForceReply

from ..utils import filters

youtube_dl_links = ["youtube", "youtu", "facebook", "soundcloud"]


@Client.on_callback_query(filters.callback_query("ytvid"), group=0)
async def callback_ytvid_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()
    await YTdl().extract(cb_message, "video")


@Client.on_callback_query(filters.callback_query("ytaudio"), group=0)
async def callback_ytaudio_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()
    await YTdl().extract(cb_message, "audio")


@Client.on_callback_query(filters.callback_query("ytmd"), group=0)
async def callback_ytmd_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()
    video_info = await YTdl().yt_media_info(cb_message)

    await cb_message.reply_text(
        "Here is the Media Info you requested: \n"	
        f"{emoji.CAT} View on nekobin.com: {video_info}"
    )


@Client.on_callback_query(filters.callback_query("download"), group=0)
async def callback_download_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()

    ack_message = await cb_message.reply_text(
        "About to start downloading the file to Local."
    )

    await Downloader().download_file(cb_message.text, ack_message, None)


@Client.on_callback_query(filters.callback_query("screens"), group=0)
async def callback_screens_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None
    await Screens().cap_screens(cb_message)
    # i think that should do... lets check?


@Client.on_callback_query(filters.callback_query("rename"), group=1)
async def callback_rename_handler(c: Client, cb: CallbackQuery):
    await cb.answer()

    params = cb.payload.split('_')
    cb_message_id = int(params[1]) if len(params) > 1 else None

    await cb.message.reply_text(
        f"RENAME_{cb_message_id}:\n"
        f"Send me the new name of the file as a reply to this message.",
        reply_markup=ForceReply(True)
    )


@Client.on_callback_query(filters.callback_query("info"), group=2)
async def callback_info_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    await cb.answer()
    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None
    m_info, neko_link = await MediaInfo().get_media_info(cb_message.text)
    if m_info:
        try:
            await cb.message.reply_document(
                caption="Here is the Media Info you requested: \n"
                        f"{emoji.CAT} View on nekobin.com: {neko_link}",
                document=m_info
            )
        finally:
            if os.path.exists(m_info):
                os.remove(m_info)


@Client.on_message(filters.reply & filters.private, group=1)
async def reply_message_handler(c: Client, m: Message):
    func_message_obj = str(m.reply_to_message.text).splitlines()[0].split("_")
    if len(func_message_obj) > 1:
        func = func_message_obj[0]
        org_message_id = int(str(func_message_obj[1]).replace(":", ""))
        org_message = await c.get_messages(m.chat.id, org_message_id)
        if func == "RENAME":
            new_file_name = m.text

            ack_message = await m.reply_text(
                "About to start downloading the file to Local."
            )

            await Downloader().download_file(org_message.text, ack_message, new_file_name)


@Client.on_message(filters.private & (filters.document | filters.video | filters.audio), group=4)
async def media_receive_handler(c: Client, m: Message):
    user_settings = await MegaUsers().get_user(m.from_user.id)
    if "f_rename_type" not in user_settings:
        await MegaUsers().update_file_rename_settings(m.from_user.id, "disk")

    fd_msg = await m.forward(
        chat_id=Common().bot_dustbin
    )

    file_link = f"https://{Common().web_fqdn}/{fd_msg.message_id}" if Common().on_heroku else \
        f"http://{Common().web_fqdn}:{Common().web_port}/{fd_msg.message_id}"

    await m.reply_text(
        text="What would you like to do with this file?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=f"{emoji.ROCKET} Streaming Link", url=file_link)],
                [InlineKeyboardButton(text=f"{emoji.PEN} Rename File",
                                      callback_data=f"prflrn_{m.chat.id}_{m.message_id}")]
            ]
        )
    )


@Client.on_callback_query(filters.callback_query("prflrn"), group=1)
async def callback_file_rename_proc_handler(c: Client, cb: CallbackQuery):
    await cb.answer()

    params = cb.payload.split('_')
    cb_message_id = int(params[1]) if len(params) > 1 else None

    await cb.message.reply_text(
        text=f"FRNM_{cb_message_id}\n"
             "Send me the new name of this file to rename it.",
        reply_markup=ForceReply(True)
    )


