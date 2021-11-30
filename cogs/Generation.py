import copy
import discord
from discord.ext import commands
import gspread
from classes.Channels import RegChannel, GenChannel
from classes.registrator import Registrator
import bot
import utils.discord_utils as discord_utils

# TODO: need to add some sort of check for cross-cog commands (Registration commands can't be used in generation channels, and vice versa)

class Generation(commands.Cog):
    def __init__(self, bot: bot.TournamentBOT):
        self.bot = bot
    
    async def send_temp_messages(self, ctx, *args):
        try:
            await ctx.send('\n'.join(args), delete_after=25)
        except discord.errors.Forbidden:
            await ctx.send(f"I do not have adequate permissions. Check `{ctx.prefix}help` for a list of the permissions that I need.")
    async def send_messages(self,ctx, *args):
        try:
            await ctx.send('\n'.join(args))
        except discord.errors.Forbidden:
            await ctx.send(f"I do not have adequate permissions. Check `{ctx.prefix}help` for a list of the permissions that I need.")
    
    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        if ctx.command not in self.bot.get_cog('Generation').get_commands(): return
        self.set_instance(ctx)

    def set_instance(self, ctx: commands.Context):
        '''
        Add a GenChannel instance into the generator_instances dictionary if it isn't present.
        '''

        channel_id = ctx.channel.id
        
        if channel_id in self.bot.generator_instances: 
            self.bot.generator_instances[channel_id].prefix = ctx.prefix
            return
        
        # self.bot.generator_instances[channel_id] = GenChannel(self.bot, ctx)

    async def cog_before_invoke(self, ctx):
        self.set_instance(ctx)
    
    async def check_callable(self, ctx: commands.Context, command):
        if ctx.channel.id in self.bot.registrator_instances:
            await ctx.send("You cannot use generation commands in registration channels.")
            return True
    
        if command == 'open': return False
        
        if ctx.channel.id not in self.bot.generator_instances:
            await ctx.send(f"You don't have an open tournament. If you'd like to open a tournament, do `{ctx.prefix}open`.")
            return True

        if command not in {'close', 'start', 'finish'} and not self.bot.generator_instances[ctx.channel.id].is_active():
            await ctx.send(f"You need to have an active tournament before using `{ctx.prefix}{command}`.")
            return True
        
        return False
    
    async def send_file(self, ctx: commands.Context, file_content, dir, filename):
        filename = filename.replace(' ', '_').lower() 
        r_file = discord_utils.create_temp_file(filename, file_content, dir=dir)
        discord_utils.delete_file(dir+filename)
        await ctx.send(file = discord.File(fp=r_file, filename=filename))

    @commands.command(aliases=['o', 'openreg', 'openregistration'])
    @commands.has_permissions(manage_guild=True)
    async def open(self, ctx: commands.Context, reg_channel_id: str, sheets_id: str, self_rating: bool = False, tournament_type: str = "SINGLE", seeding: bool = True, bracket: bool = False):
        '''
        Opens a channel for tournament registrations.
        '''
        if await self.check_callable(ctx, 'open'): return 

        try:
            reg_channel_id = int(reg_channel_id.lstrip("<#").rstrip(">"))
        except ValueError:
            return await ctx.send("Invalid registration channel ID; the registration channel ID can either be the number ID from `Copy ID` or the `#channel-name`.")
        
        if reg_channel_id == ctx.channel.id:
            return await ctx.send("You cannot set the registration channel to this channel.")
        if reg_channel_id in self.bot.generator_instances:
            return await ctx.send("You cannot set this channel as the registration channel because this channel is already being used as a generation channel.")
        if reg_channel_id in self.bot.registrator_instances:
            return await ctx.send("You cannot set this channel as the registration channel because it is already being used as a registration channel.")

        if not ctx.guild.get_channel(reg_channel_id):
            return await ctx.send("The registration channel you provided was invalid.")
        
        tournament_type = discord_utils.convert_str_to_tournament(tournament_type)

        
        # if self.bot.generator_instances[ctx.channel.id].is_open():
        #     #did `,reset` but there's an existing open tournament instance
        #     pass
        
        init_mes = ctx.send("Setting up Google Spreadsheet...")
                
        self.bot.generator_instances[ctx.channel.id] = GenChannel(self.bot, ctx)
        self.bot.generator_instances[ctx.channel.id].setup(tournament_type, reg_channel_id, sheets_id, self_rating, seeding, bracket)

        self.bot.registrator_instances[reg_channel_id] = RegChannel(self.bot, ctx)
        try:
            self.bot.registrator_instances[reg_channel_id].setup(ctx.channel.id, sheets_id, self_rating, registrator=Registrator(sheets_id, use_rating=self_rating))
        except Exception as error:
            await init_mes.delete()
            if isinstance(error, gspread.exceptions.APIError):
                err_status = error.response.json()['error']['status']
                if err_status == 'NOT_FOUND':
                    return await ctx.send("The Google Sheets ID you provided was invalid or I cannot access it. Check that your Sheets ID is correct (it should be a long string of random characters after the `/d/` in the Sheets URL).\nAlso, make sure that the spreadsheet is shared with my service client (`tournament-generator@tournament-generator-332215.iam.gserviceaccount.com`) with **edit** access.")
                elif err_status == 'PERMISSION_DENIED':
                    return await ctx.send("I cannot access the Spreadsheet you've provided because I lack adequate permissions. Make sure that the spreadsheet is shared with my service client (`tournament-generator@tournament-generator-332215.iam.gserviceaccount.com`) with **edit** access.")
            raise error
        
        await init_mes.delete()
        await ctx.send(f"I am now watching registrations in <#{reg_channel_id}>.")
    
    @open.error
    async def open_error(self, ctx: commands.Context, error):
        self.set_instance(ctx)
        if await self.check_callable(ctx, 'open'): return 

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{ctx.prefix}open [registrationChannelID] [sheetsID] (rating=False) (seeding=True) (bracket=True)`")
        elif isinstance(error, commands.BadArgument):
            await self.send_messages(ctx, f"Error processing paramters: {', '.join(error.args)}", 
                f"Usage: `{ctx.prefix}open [registrationChannelID] [sheetsID] (rating=False) (seeding=True) (bracket=True)`")

    @commands.command(aliases=['endreg', 'closereg', 'stopreg'])
    async def close(self, ctx: commands.Context):
        '''
        Closes the registration channel.
        ''' 
        if await self.check_callable(ctx, "close"): return 

        reg_channel_id = self.bot.generator_instances[ctx.channel.id].get_reg_channel()
        mes = self.bot.registrator_instances[reg_channel_id].close_reg()
        await ctx.send("Registrations have been closed.")
        await ctx.guild.get_channel(reg_channel_id).send(mes)

    @commands.command(aliases=['initialize', 'init', 'create', 'begin'])
    @commands.has_permissions(manage_guild=True)
    async def start(self, ctx: commands.Context, sheets_id: str = None, self_rating: bool = False, tournament_type: str = "SINGLE", seeding = True, bracket = True):
        '''
        Load player registrations and initialize the tournament's first round.
        '''
        if sheets_id is not None:
            tournament_type = discord_utils.convert_str_to_tournament(tournament_type)
            self.bot.generator_instances[ctx.channel.id] = GenChannel(self.bot, ctx)
            init_mes = await ctx.send("Loading registrations from Google Sheets...")
            self.bot.generator_instances[ctx.channel.id].skip_reg_setup(tournament_type, sheets_id, self_rating, seeding, bracket)
        
        if await self.check_callable(ctx, "start"): return

        if self.bot.generator_instances[ctx.channel.id].reg_channel is None:
            await ctx.send(f"You need to have an open tournament and have finished player registrations before using `{ctx.prefix}start`.")
            return True
        reg_open = self.bot.generator_instances[ctx.channel.id].reg_open()
        if reg_open is None or reg_open is True:
            await ctx.send(f"You need to close player registrations before using `{ctx.prefix}start`. To close player registrations, do `{ctx.prefix}close`.")
            return True

        mes, round, file_content = self.bot.generator_instances[ctx.channel.id].start_tournament()
        try:
            await init_mes.edit(content="Registrations loaded.")
        except:
            pass
        if not file_content:
            return await ctx.send(mes)
        dir = './temp_files/'
        filename = f"{round}_matchups-{ctx.channel.id}.txt"
        await ctx.send(mes)
        await self.send_file(ctx, file_content, dir, filename)
    
    @commands.command(aliases=['a', 'adv'])
    @commands.has_permissions(manage_guild=True)
    async def advance(self, ctx: commands.Context, *, players_arg):
        '''
        Advance a group of players to the next round.
        '''
        #TODO: process different player args (have to split by newlines or another special character)
        if await self.check_callable(ctx, "advance"): return
        players = players_arg.split("\n")
        players = [player.strip().lstrip("<@").lstrip("<@!").rstrip(">") for player in players]

        mes = self.bot.generator_instances[ctx.channel.id].advance_players(players)
        await ctx.send(mes)
    
    @advance.error
    async def advance_error(self, ctx: commands.Context, error):
        self.set_instance(ctx)
        if await self.check_callable(ctx, "advance"): return

        if isinstance(error, commands.MissingRequiredArgument):
            await self.send_temp_messages(ctx, f"Usage: `{ctx.prefix}advance [player, ...]`")
    
    @commands.command(aliases=['ua', 'unadv'])
    @commands.has_permissions(manage_guild=True)
    async def unadvance(self, ctx: commands.Context, *, players_arg):
        '''
        Unadvance a group of players from the next round's advanced pool.
        '''
        #TODO: process different player args (have to split by newlines or another special character)
        if await self.check_callable(ctx, "unadvance"): return
        players = players_arg.split("\n")
        players = [player.strip().lstrip("<@").lstrip("<@!").rstrip(">") for player in players]

        mes = self.bot.generator_instances[ctx.channel.id].unadvance_players(players)
        await ctx.send(mes)
    
    @unadvance.error
    async def unadvance_error(self, ctx: commands.Context, error):
        self.set_instance(ctx)
        if await self.check_callable(ctx, "unadvance"): return

        if isinstance(error, commands.MissingRequiredArgument):
            await self.send_temp_messages(ctx, f"Usage: `{ctx.prefix}unadvance [player, ...]`")
    
    @commands.command(aliases=['increment', 'next'])
    @commands.has_permissions(manage_guild=True)
    async def nextround(self, ctx: commands.Context):
        '''
        Move on to the next round.
        '''
        if await self.check_callable(ctx, "nextround"): return

        if self.bot.generator_instances[ctx.channel.id].is_finished():
            return await self.finish(ctx)

        round_finished, mes, round, file_content = self.bot.generator_instances[ctx.channel.id].next_round()
        if file_content is None:
            return await ctx.send(mes)
        dir = './temp_files/'
        filename = f"{round}-{ctx.channel.id}.txt"
        await ctx.send(mes)
        await self.send_file(ctx, file_content, dir, filename)

        if round_finished:
            self.bot.generator_instances[ctx.channel.id].update_round_results()
    
    @commands.command(aliases=['rs', 'roundstatus'])
    @commands.has_permissions(manage_guild=True)
    async def status(self, ctx: commands.Context):
        '''
        Get the status (matchups that have finished and matchups that are still in progress) of the current round.
        '''

        if await self.check_callable(ctx, "status"): return

        mes, round, file_content = self.bot.generator_instances[ctx.channel.id].round_status()

        if file_content is None:
            return await ctx.send(mes)

        dir = './temp_files/'
        filename = f"{round}_status-{ctx.channel.id}.txt"
        await ctx.send(mes)
        await self.send_file(ctx, file_content, dir, filename)


    @commands.command(aliases=['rr', 'roundresults', 'res'])
    @commands.has_permissions(manage_guild=True)
    async def results(self, ctx: commands.Context, round = -1):
        '''
        Get the results of a specific round (all matchups and winners of each matchup).
        '''
        if await self.check_callable(ctx, "results"): return

        mes, file_content = self.bot.generator_instances[ctx.channel.id].round_results(round)
        if file_content is None:
            return await ctx.send(mes)
        dir = './temp_files/'
        filename = f"{mes}_results-{ctx.channel.id}.txt"
        await self.send_file(ctx, file_content, dir, filename)

    @commands.command(aliases=['stop', 'done', 'reset', 'endtournament', 'clear', 'end'])
    @commands.has_permissions(manage_guild=True)
    async def finish(self, ctx: commands.Context):
        '''
        Finish the tournament, update the results to the Google Sheet, and clear the generation instance.
        '''
        if await self.check_callable(ctx, "finish"): return

        gen_instance = self.bot.generator_instances[ctx.channel.id]
        if not gen_instance.is_active() and not gen_instance.is_open():
            return await ctx.send("You don't have an active tournament to stop.")

        if gen_instance.is_finished():
            gen_instance.end_tournament()
            await ctx.send(f"Tournament has been ended. Congratulations to the winner: {gen_instance.get_winner().get_displayName()}!")
            gen_instance.update_round_results()
        else:
            await ctx.send(f"Tournament has been reset. Do `{ctx.prefix}open` to open a new tournament.")

        reg_channel = gen_instance.get_reg_channel()
        self.bot.generator_instances.pop(ctx.channel.id)
        try:
            self.bot.registrator_instances.pop(reg_channel)
        except KeyError: #registration instance doesn't exist (registration was skipped)
            pass
    
    @commands.command(aliases=['getsheet', 'googlesheet', 'sheets', 'spreadsheet'])
    @commands.has_permissions(manage_guild=True)
    async def sheet(self, ctx: commands.Context):
        '''
        Get a link of the spreadsheet associated with the tournament.
        '''
        if await self.check_callable(ctx, "sheet"): return

        return await ctx.send(self.bot.generator_instances[ctx.channel.id].get_sheet_link())

def setup(bot):
    bot.add_cog(Generation(bot))