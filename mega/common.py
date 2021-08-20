import ast
import configparser
import os


class Common:
    def __init__(self):
        """Common: are commonly shared variables across the application that is loaded from the config file or env."""
        self.working_dir = "mega/working_dir"
        self.on_heroku = False

        self.is_env = bool(os.environ.get("ENV", None))
        if self.is_env:
            self.tg_app_id = int(os.environ.get("TG_APP_ID"))
            self.tg_api_key = os.environ.get("TG_API_HASH")

            self.bot_session = ":memory:"
            self.bot_api_key = os.environ.get("TG_BOT_TOKEN")
            self.bot_dustbin = int(os.environ.get("TG_DUSTBIN_CHAT", "-100"))
            self.allowed_users = ast.literal_eval(
                os.environ.get("ALLOWED_USERS", '[]')
            )

            
