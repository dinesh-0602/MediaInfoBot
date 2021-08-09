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
#from mega.helpers.uploader import UploadFiles
#from mega.helpers.downloader import Downloader
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


@Client.on_callback_query(filters.callback_query("screens"), group=0)
async def callback_screens_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None
    await Screens().cap_screens(cb_message)
    # i think that should do... lets check?


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


