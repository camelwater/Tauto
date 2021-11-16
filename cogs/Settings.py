from utils.discord_utils import SETTING_VALUES, SPLIT_DELIM
import discord
from discord.ext import commands
import bot
import utils.gen_utils as gen_utils
import os
from fnmatch import fnmatch
RESERVED_DELIM = SPLIT_DELIM

class Settings(commands.Cog):
    def __init__(self, bot: bot.TournamentBOT):
        self.bot = bot
    
    @commands.command(aliases=['h'])
    async def help(self, ctx: commands.Context):
        link1 = "[Introduction](https://github.com/camelwater/tournament-generator/blob/main/README.md)"
        link2 = "[Documentation](https://github.com/camelwater/tournament-generator/wiki)"
        e = discord.Embed(title="Help", description=link1+'\n'+link2)
        # e.add_field(name='\u200b', value= link1 +'\n'+link, inline=False)

        await ctx.send(embed=e)
    
    @commands.command(aliases=['info'])
    async def about(self, ctx):
        e = discord.Embed(title='Table BOT', description='')

        e.add_field(name='\u200b', value=f'_WRITTEN IN:_ python with discord.py v1.7.3\n\
                        _LINES OF CODE:_ {count_LOC()}\n_SERVER:_ AWS - Amazon Linux 2 AMI', inline=False)

        link = "[GitHub Repository](https://github.com/camelwater/tournament-generator)"
        e.add_field(name='\u200b', value= link, inline=False)

        await ctx.send(embed=e)
    
    @commands.command(aliases=['getprefixes', 'pxs'])
    async def prefixes(self, ctx: commands.Context):
        prefixes = self.bot.get_guild_prefixes(ctx.guild)
        mes = "{} prefixes:\n".format(f'[{ctx.guild.name}]')
        if len(prefixes) == 0:
            mes+="No prefixes."
        for i, p in enumerate(prefixes):
            mes+=f"{i+1}. {p}\n"
        await ctx.send(f"```css\n{mes}```")

    @commands.group(invoke_without_command=True, aliases=['px'],  case_insensitive=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx: commands.Context):
        px = ctx.prefix
        await ctx.send(f"```Usage:\n{px}prefix add <prefix>\n{px}prefix remove <prefix>\n{px}prefix set <prefix>\n{px}prefix reset```")
    
    @prefix.command(aliases=['+'])
    @commands.has_guild_permissions(manage_guild=True)
    async def add(self, ctx: commands.Context, *, prefix: str = None):
        if prefix is None:
            await ctx.send("You need to specify a prefix to be added.")
            return
        if RESERVED_DELIM in prefix:
            return await ctx.send("You cannot add this prefix because it contains forbidden characters.")
        mes = self.bot.add_prefix(ctx.guild.id, prefix)
        
        await ctx.send(mes)
    
    @prefix.command(aliases=['-'])
    @commands.has_guild_permissions(manage_guild=True)
    async def remove(self, ctx: commands.Context, *, prefix: str = None):
        if prefix is None:
            guild_prefixes = ''
            pfxs = self.bot.get_guild_prefixes(ctx.guild)
            if len(pfxs) == 0:
                return await ctx.send(f"You don't have any prefixes registered. You can add or set custom prefixes with `{ctx.prefix}prefix`.")
            for p in pfxs:
                guild_prefixes+=f"- `{p}`\n"
            await ctx.send(f"You need to specify a prefix to be removed:\n{guild_prefixes}")
            return
        
        mes = self.bot.remove_prefix(ctx.prefix, ctx.guild.id, prefix)
        await ctx.send(mes)
    
    @prefix.command(name='set')
    @commands.has_guild_permissions(manage_guild=True)
    async def _set(self, ctx: commands.Context, *, prefix: str = None):
        if RESERVED_DELIM in prefix:
            return await ctx.send("You cannot set this prefix because it contains forbidden characters.")

        mes = self.bot.set_prefix(ctx.guild.id, prefix)
        await ctx.send(mes)
    
    @prefix.command(name='reset')
    @commands.has_guild_permissions(manage_guild=True)
    async def _reset(self, ctx: commands.Context):
        mes = self.bot.reset_prefix(ctx.guild.id)
        await ctx.send(mes)
    
    @commands.command(aliases=['sets'])
    @commands.guild_only()
    async def settings(self, ctx: commands.Context, mes=True):
        settings = self.bot.get_guild_settings(ctx.guild.id)
        spaces = max([len(k[0]) for k in settings.items()])+1
        out = f'asciidoc\n== [{ctx.guild.name}] server settings =='
        for name, val in settings.items():
            if name in ['defaultOpen', 'defaultRandom']:
                val = bool(val)
            
            out+="\n{}{}:: {}".format(name, " "*(spaces-len(name)), val)
        
        if mes:
            await ctx.send(f"```{out}```")
        else:
            return f"```{out}```"

    @commands.command(aliases=['setting'])
    @commands.has_guild_permissions(manage_guild=True)
    async def set(self, ctx: commands.Context, settingType: str = None, *, default: str=None):
        if settingType is None:
            px = ctx.prefix
            await ctx.send(f"```asciidoc\n[Usage]\n{px}set <settingName> <value>\n{px}set reset <settingName>\nSee `{px}settings' for a list of customizable settings.\n```")
            return
        settingType = settingType.strip()
        if settingType.lower() in ['reset', 'clear']:
            if default: #resetting specific setting (default becomes settingType)
                mes = self.bot.set_setting(ctx.guild.id, correct_settingName(default), None)
            else: #resetting all settings
                mes = self.bot.reset_settings(ctx.guild.id)
            return await ctx.send(mes)
        
        settingType = correct_settingName(settingType)
        avail_settings = get_avail_settings(settingType)
        
        if not avail_settings:
            return await ctx.send("Invalid setting `{}`. Here are the customizable settings:\n{}".format(settingType, await self.settings(ctx, mes=False)))

        if default is None:
            if not avail_settings:
                await ctx.send("Invalid setting `{}`. Here are the customizable settings:\n{}".format(settingType, await self.settings(ctx, mes=False)))
            else:
                await(await ctx.send(f"Specify a setting value for `{settingType}`. The value can be any of the following"
                                + f":\n{avail_settings}")).delete(delay=60)
            return

        valid = False
        if settingType in ['defaultOpen', 'defaultRandom']:
            if default.isnumeric():
                default = int(default)
                if default in SETTING_VALUES[settingType]: valid = True
            else:
                # for k, v in SETTING_VALUES[settingType].items():
                #     if default.lower() in map(lambda l: l.lower(), v.values()):
                #         default = k
                #         valid = True
                #         break
                if default.lower() in SETTING_VALUES[settingType].keys(): valid = True
                
        else:
            # other settings
            pass

        if not valid:
            await ctx.send(f"Invalid value `{default}` for setting `{settingType}`. The value must be"+
                        f"one of the following:\n{get_avail_settings(settingType)}")
            return

        mes = self.bot.set_setting(ctx.guild.id, settingType, default)
        await ctx.send(mes)
    
def get_avail_settings(settingType):
    setting_vals = SETTING_VALUES.get(settingType)
    if setting_vals is None:
        return None

    ret = ""
    if settingType in ['defaultOpen', 'defaultRandom']:
        setting_vals = list(gen_utils.chunks(list(setting_vals.keys()), len(setting_vals)))
        for ind, values in enumerate(setting_vals):
            ret+=f'**{bool(ind)}**: {" | ".join(map(lambda orig: f"`{orig}`", values))}'

    else:
        for ind, dic in setting_vals.items():
            ret+='`{}.` {}\n'.format(ind, " | ".join(map(lambda orig: "`{}`".format(orig), dic.values())) if settingType in ['graph', 'style']
                                            else f'`{dic}`')
    
    return ret

def correct_settingName(setting: str):
    try:
        assert(setting in SETTING_VALUES)
        return setting
    except AssertionError:
        try:
            lowered_keys = list(map(lambda l: l.lower(), SETTING_VALUES.keys()))
            assert(setting.lower() in lowered_keys)
            return list(SETTING_VALUES.keys())[lowered_keys.index(setting.lower())]
        except AssertionError:
            return setting

def count_LOC():
    LOC_count = 0
    for dir in ['.', './cogs', './utils', './classes']:
        for file in os.listdir(dir):   
            if fnmatch(file, '*.py'):
                with open(f"{dir}/{file}", encoding='utf-8') as f:
                    for _ in f:
                        LOC_count+=1

    return LOC_count
    
def setup(bot):
    bot.add_cog(Settings(bot))