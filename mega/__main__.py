import logging
import asyncio
from aiohttp import web
from pyrogram import idle
#from mega.telegram import MegaDLBot
#from mega.webserver import web_server
from mega.common import Common





if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logging.error("KeyboardInterruption: Services Terminated!")
