from pyrogram import filters, emoji, Client
from pyrogram.types import Message
#from mega.database.files import MegaFiles
#from mega.database.users import MegaUsers
from ...telegram import Common


@Client.on_message(filters.command("start", prefixes=["/"]))
async def start_message_handler(c: Client, m: Message):
    await m.reply_text(
        text=f"Hello! My name is Megatron {emoji.MAN_BOWING_DARK_SKIN_TONE}"
    )


@Client.on_message(group=-1)
async def stop_user_from_doing_anything(_, message: Message):
    allowed_users = Common().allowed_users
    if allowed_users and str(message.from_user.id) not in allowed_users:
        message.stop_propagation()
    else:
        message.continue_propagation()
