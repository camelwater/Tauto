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
from typing import Tuple, Dict, List, Any
import atexit
import classes.Channels as Channels

import argparse
from utils.discord_utils import SETTING_VALUES, SPLIT_DELIM, DEFAULT_PREFIXES
import classes.Errors as Errors
import gspread


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
                defaultOpen BIT,
                defaultRandom BIT)''')

def fetch_prefixes_and_settings() -> Tuple[Dict, Dict]:
    cur.execute('SELECT * FROM servers')
    server_rows = cur.fetchall()
    server_pxs = {k[0]: k[1] for k in server_rows}
    # print(server_rows)
    server_sets = {k[0]: {"defaultOpen": k[2] if k[2] is not None else 1, "defaultRandom": k[3] if k[3] is not None else 0} for k in server_rows}
   
    return {k: (p.split(SPLIT_DELIM) if p else []) for k, p in server_pxs.items()}, server_sets

def callable_prefix(bot, msg: discord.Message, mention=True) -> List[str]:
    base = list()
    default = DEFAULT_PREFIXES
    if msg.guild is None:
        base = default
    else:
        base.extend(bot.prefixes.get(msg.guild.id, default))
        # base.append('$')

    if mention:
        return commands.when_mentioned_or(*base)(bot, msg)
    return base


class TournamentBOT(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = callable_prefix , case_insensitive = True, intents = discord.Intents.all(), help_command = None)
        self.BOT_ID = 907717733582532659
        self.presences = cycle([',help', "{} active tournaments"])
        # self.prefixes, self.settings = fetch_prefixes_and_settings()
        self.generator_instances: Dict[int, Channels.GenChannel] = dict() #gen_channel_id: GenChannel instance
        self.registrator_instances: Dict[int, Channels.RegChannel] = dict() #reg_channel_id: RegChannel instance

        for ext in INIT_EXT:
            self.load_extension(ext)

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
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I am missing these required permissions:" + ", ".join(error.missing_perms))
        elif isinstance(error, Errors.RegChannelSetupError):
            await ctx.send(f"You have not set up this channel to be a registration channel. If you'd like to set this channel as a registration channel, use `{ctx.prefix}open`.", delete_after=7)
        elif isinstance(error, gspread.exceptions.APIError):
            await ctx.send(f"There was an error with the Google API. Try again later.")
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
                            VALUES (?, ?, ?, ?)''', 
                            (server.id, SPLIT_DELIM.join(DEFAULT_PREFIXES), 1, 0)) # id, prefixes, defaultOpen, defaultRandom (default value)
            conn.commit()

        self.prefixes, self.settings = fetch_prefixes_and_settings()

        try:
            self.cycle_presences.start()
        except RuntimeError:
            print("cycle_presences task failed to start")
        
    async def on_guild_join(self, guild: discord.Guild):
        cur.execute('''INSERT OR IGNORE INTO servers
                        VALUES (?, ?, ?, ?)''',
                        (guild.id, SPLIT_DELIM.join(DEFAULT_PREFIXES), 1, 0)) #id, prefixes, defaultOpen, defaultRandom
        conn.commit()

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
        return sum([1 for gen_channel in list(self.generator_instances.values()) if gen_channel.is_active()])

    def get_guild_prefixes(self, guild, local_callable = callable_prefix) -> List[str]:
        temp_msg = discord.Object(id=0)
        temp_msg.guild = guild

        return local_callable(self, temp_msg, mention=False)
    
    def add_prefix(self, guild, prefix):
        if len(self.prefixes.get(guild, [])) >=5:
            return "You cannot have more than 5 custom prefixes."
        if prefix in [f'<@!{self.BOT_ID}>', f'<@{self.BOT_ID}>']:
            return "My mention is a default prefix and cannot be added as a custom prefix."
        if prefix in self.prefixes.get(guild, []):
            return f"`{prefix}` is already registered as a prefix."
        
        prefixes = self.prefixes.get(guild, [])
        prefixes.append(prefix)
        self.prefixes[guild] = prefixes
        cur.execute('''UPDATE servers 
                        SET prefixes=? 
                        WHERE id=?''',
                    (SPLIT_DELIM.join(prefixes), guild))
        conn.commit()
        
        return f"`{prefix}` has been registered as a prefix."
    
    def remove_prefix(self, ctx_prefix, guild, prefix):
        if prefix in [f'<@!{self.BOT_ID}>', f'<@{self.BOT_ID}>']:
            return "My mention is a default prefix and cannot be removed."

        try:
            self.prefixes[guild].remove(prefix)
            cur.execute('''UPDATE servers 
                            SET prefixes=? 
                            WHERE id=?''',
                        (SPLIT_DELIM.join(self.prefixes[guild]) if len(self.prefixes[guild])>0 else None, guild))
            conn.commit()

            return f"Prefix `{prefix}` has been removed." + (f' You must use my mention, {self.user.mention}, as the prefix now.' if len(self.prefixes[guild])==0 else "")
        except KeyError:
            return f"You don't have any custom prefixes registered. You can add or set custom prefixes with `{ctx_prefix}prefix`."
        except ValueError:
            return f"`{prefix}` is not a registered prefix."
        
    def set_prefix(self, guild, prefix):
        if not prefix:
            self.prefixes[guild] = []
            cur.execute('''UPDATE servers 
                            SET prefixes=? 
                            WHERE id=?''',
                        (None, guild))
            conn.commit()
            return f"All prefixes have been removed. Use my mention, {self.user.mention}, as the prefix."
        
        if prefix in [f'<@!{self.BOT_ID}>', f'<@{self.BOT_ID}>']:
            return "The bot mention is a default prefix and cannot be set as a custom prefix."
        
        self.prefixes[guild] = [prefix]
        cur.execute('''UPDATE servers 
                        SET prefixes=? 
                        WHERE id=?''', 
                    (str(prefix), guild))
        conn.commit()

        return f"`{prefix}` has been set as the prefix."
    
    def reset_prefix(self, guild):
        self.prefixes[guild] = copy.copy(DEFAULT_PREFIXES)
        cur.execute('''UPDATE servers 
                        SET prefixes=? 
                        WHERE id=?''',
                    (SPLIT_DELIM.join(DEFAULT_PREFIXES), guild))
        conn.commit()

        return "Server prefixes have been reset to default."

    def get_guild_settings(self, guild) -> Dict[str, Any]:
        default = {'defaultOpen': 1, 'defaultRandom': 0}

        return self.settings.get(guild, default)
    
    def reset_settings(self, guild):
        default = {'defaultOpen': 1, 'defaultRandom': 0}
        self.settings[guild] = default

        cur.execute('''UPDATE servers 
                        SET defaultOpen=?, defaultRandom=?
                        WHERE id=?''',
                    (default.get('defaultOpen'), default.get('defaultRandom'), guild))
        conn.commit()

        return "Server settings have been reset to default values."
    
    def set_setting(self, guild, setting, default):
        default_sets = {'defaultOpen': 1, 'defaultRandom': 0}
        if not default:
            try:
                default = default_sets.get(setting)
                self.settings[guild][setting] = default
            except KeyError:
                pass

            cur.execute(f'''UPDATE servers 
                            SET {setting}=? 
                            WHERE id=?''',
                            (default, guild))
            conn.commit()

            return f"`{setting}` setting restored to default."

        if setting in ['defaultOpen', 'defaultRandom']:
            default = SETTING_VALUES[setting][default]

        try:
            self.settings[guild][setting] = default
        except KeyError:
            self.settings[guild] = {}
            self.settings[guild][setting] = default
        
        cur.execute(f'''UPDATE servers 
                        SET {setting}=? 
                        WHERE id=?''',
                        (default, guild))
        conn.commit()
        # cur.execute('''SELECT * 
        #                 FROM servers''')
        # print(cur.fetchall())


        return "`{}` setting set to `{}`.".format(setting, bool(default) if setting in {'defaultOpen', 'defaultRandom'} else default)
    
    def get_setting(self, type, guild, raw = False):
        default = {'defaultOpen': 1, 'defaultRandom': 0}
        setting = self.settings.get(guild, default).get(type)
        if raw:
            return setting
        if type in {'defaultOpen', 'defaultRandom'}:
            return bool(setting)
        return setting
    
    async def close(self):
        await super().close()

    def run(self):
        super().run(KEY, reconnect=True)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('key', metavar='KEY', type=str, nargs='?')
    return parser.parse_args().key

if __name__ == "__main__":
    bot_key = parse_args()
    if bot_key: KEY = bot_key

    bot = TournamentBOT()
    bot.run()

    @atexit.register
    def on_exit():
        conn.close()

