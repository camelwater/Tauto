import discord
from discord.ext import commands, tasks
import logging
from dotenv import dotenv_values
from logging.handlers import RotatingFileHandler
import copy
from itertools import cycle
from datetime import datetime, timedelta
import traceback as tb
import sqlite3
from typing import Tuple, Dict, List


creds = dotenv_values(".env.testing") or dotenv_values(".env") #.env.testing for local testing, .env for deployment
KEY = creds['KEY']
LOG_LOC = 'logs/logs.log'

INIT_EXT = ['cogs.Registration', 'cogs.Generation', 'cogs.Settings']

handlers = [RotatingFileHandler(filename=LOG_LOC, 
            mode='w', 
            maxBytes=512000, 
            backupCount=4)
           ]
logging.basicConfig(handlers = handlers,
                    format='%(asctime)s %(levelname)s -> %(message)s\n',
                    level=logging.ERROR)
log = logging.getLogger(__name__)

conn = sqlite3.connect('resources/database.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS servers (
                id integer PRIMARY KEY,
                prefixes text, 
                registration_channel integer, 
                generation_channel integer, 
                defaultOpen boolean)''')

SPLIT_DELIM = '{d/D17¤85xu§ey¶}'
DEFAULT_PREFIXES = ['?', '!']

def fetch_prefixes_and_settings() -> Tuple[Dict, Dict]:
    cur.execute('SELECT * FROM servers')
    server_rows = cur.fetchall()
    server_pxs = {k[0]: k[1] for k in server_rows}
    server_sets = {int(k[0]): {"registration_channel": k[2], "generation_channel": k[3], "defaultOpen": k[4] or True} for k in server_rows}
   
    return {int(k): (p.split(SPLIT_DELIM) if p else []) for k, p in server_pxs.items()}, server_sets

def callable_prefix(bot, msg: discord.Message, mention=True) -> List[str]:
    base = []
    default = DEFAULT_PREFIXES
    if msg.guild is None:
        base = default
    else:
        base.extend(bot.prefixes.get(msg.guild.id, default))
        # base.append('$')

    if mention:
        return commands.when_mentioned_or(*base)(bot, msg)
    return base

class GenBot(commands.Bot):
    def __init__(self):
        super().init(command_prefix = callable_prefix , case_insensitive = True, intents = discord.Intents.all(), help_command = None)
        self.presences = cycle(['!help', "{} active tournaments"])
        self.prefixes, self.settings = fetch_prefixes_and_settings()
        self.tournament_instances = {}

    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            if not ctx.guild:
                await(await ctx.send(f"I don't recognize that command. Use `{ctx.prefix}help` for a list of available commands.")).delete(delay=25)
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await(await ctx.send("This command cannot be used in DMs.")).delete(delay=7)
        elif isinstance(error, commands.MissingPermissions):
            await(await ctx.send(f"Sorry {ctx.author.mention}, you don't have permission to use this command.")).delete(delay=10.0)
        elif isinstance(error, commands.CommandOnCooldown):
            await(await ctx.send(f"This command can only be used once every {error.cooldown.per:.0f} seconds. You can retry in {error.retry_after:.1f} seconds.")).delete(delay=7)
        elif isinstance(error, commands.MaxConcurrencyReached):
            await(await ctx.send(f"This command can only be used by {error.number} user at a time. Try again later.")).delete(delay=7)
        elif isinstance(error, commands.MissingRequiredArgument):
            pass
            #raise error
        elif isinstance(error, commands.errors.ExpectedClosingQuoteError):
            await(ctx.send("Bad command input: missing a closing `\"`.", delete_after=10))
        else:
            await ctx.send(f"An unidentified internal bot error occurred. Wait a bit and try again later.\nIf this issue persists, `{ctx.prefix}reset` the table.")
            error_tb = ''.join(tb.format_exception(type(error), error, error.__traceback__))
            error_tb = error_tb[:error_tb.find('\nThe above exception was the direct cause of the following exception:')]
            log.error(msg=f"in command: {ctx.command}\n{error_tb}")
            raise error

    async def on_ready(self):
        print(f"Bot logged in as {self.user}")
        for server in self.guilds:
            cur.execute('''INSERT OR IGNORE INTO servers
                            VALUES (?, ?, ?, ?, ?)''', 
                            (server.id, SPLIT_DELIM.join(DEFAULT_PREFIXES), None, None, True)) # id, registration_channel, generation_channel, defaultOpen (default values)
            conn.commit()

        self.prefixes, self.settings = fetch_prefixes_and_settings()

        try:
            self.cycle_presences.start()
        except RuntimeError:
            print("cycle_presences task failed to start")

    @tasks.loop(seconds = 15)
    async def cycle_presences(self):
        next_pres = next(self.presences)
        if "active" in next_pres:
            active_tournaments = self.count_active_tournaments()
            if active_tournaments == 0:
                next_pres = next(self.presences)
            else:
                next_pres = next_pres.format(active_tournaments)
                if active_tournaments == 1: next_pres = next_pres.replace("tournaments", "tournament")

        pres = discord.Activity(type=discord.ActivityType.watching, name=next_pres)
        await self.change_presence(status=discord.Status.online, activity=pres)
    
    def count_active_tournaments(self):
        

    

    

