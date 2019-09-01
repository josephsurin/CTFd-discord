import asyncio
import sys
from discord.ext import commands

from bot import log
from bot.constants import db_uri, token
from bot.database.sql import get_sqlalchemy_engine, get_sqlalchemy_session, get_sqlalchemy_tables
import bot.display.embed as display
from bot.manage.discord_data import get_channel


class CTFdBot:

    def __init__(self):
        """ Discord Bot to catch CTFd events made by zTeeed """
        self.bot = commands.Bot(command_prefix='>>')
        self.channel = None
        self.lock = False

        self.bot.db = lambda: None  # empty object
        self.bot.db.session = None
        self.bot.db.tables = None
        self.bot.db.tag = None  # hash of string composed of last challenge solve user id and challenge id

    async def cron(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if not self.lock and self.channel is not None:
                log.debug('CTFdBot open')
                await display.cron(self)
            else:
                log.debug('RootMeBot locked')
            await asyncio.sleep(1)

    def catch(self):
        @self.bot.event
        async def on_ready():
            self.channel = get_channel(self.bot)
            engine, base = get_sqlalchemy_engine(db_uri)
            await display.ready(self, engine)
            self.bot.db.session = get_sqlalchemy_session(engine)
            self.bot.db.tables = get_sqlalchemy_tables(base)

        @self.bot.command(description='Show ranking of CTFd (20 first players)')
        async def scoreboard(context):
            """ """
            await display.scoreboard(self)

        @self.bot.command(description='Show ranking of CTFd.')
        async def scoreboard_complete(context):
            """ """
            await display.scoreboard(self, all_players=True)

        @self.bot.command(description='Show list of categories.')
        async def categories(context):
            """ """
            await display.categories(self)

        @self.bot.command(description='Show list of challenges from a category.')
        async def category(context):
            """ <category> """
            await display.category(self, context)

        @self.bot.command(description='Return who solved a specific challenge.')
        async def problem(context):
            """ <challenge> """
            await display.problem(self, context)

        @self.bot.command(description='Return who solved a specific challenge.')
        async def who_solved(context):
            """ <challenge> """
            await display.who_solved(self, context)

        @self.bot.command(description='Return challenges solved grouped by users for last day.')
        async def solved_last_days(context):
            """ <number_of_days> (<username>) """
            await display.last_days(self, context)

        @self.bot.command(description='Return difference of solved challenges between two users.')
        async def diff(context):
            """ <username1> <username2> """
            await display.diff(self, context)

        @self.bot.command(description='Flush all data from bot channel excepted events')
        async def flush(context):
            """ """
            await display.flush(self, context)

    def start(self):
        if token == 'token':
            log.warn('Please update your token in ./bot/constants.py')
            sys.exit(0)
        self.catch()
        self.bot.loop.create_task(self.cron())
        self.bot.run(token)


if __name__ == "__main__":
    bot = CTFdBot()
    bot.start()