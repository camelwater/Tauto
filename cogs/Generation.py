import discord
from discord.ext import commands
from generator import Generator
from Channels import RegChannel, GenChannel

# TODO: need to add some sort of check for cross-cog commands (Registration commands can't be used in generation channels, and vice versa)

class Generation(commands.Cog):
    def __init__(self, bot):
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
    
    async def set_instance(self, ctx: commands.Context):
        '''
        Add a GenChannel instance into the generator_instances dictionary if it isn't present.
        '''

        channel_id = ctx.channel.id
        
        if channel_id in self.bot.generator_instances: 
            self.bot.channel_instances[channel_id].prefix = ctx.prefix
            return

        self.bot.generator_instances[channel_id] = GenChannel(self.bot, ctx)

    async def cog_before_invoke(self,ctx):
        self.set_instance(ctx)

    @commands.command(aliases=['o', 'register'])
    async def open(self, ctx: commands.Context, reg_channel_id: int, sheets_id: str, self_rating: bool = False):
        '''
        Opens a channel for tournament registrations.
        '''
        if reg_channel_id == ctx.channel.id:
            return await ctx.send("You cannot set the registration channel to this channel.")
        if reg_channel_id in self.bot.generator_instances:
            return await ctx.send("You cannot set this channel as the registration channel because this channel is already being used as a generation channel.")
        if reg_channel_id in self.bot.registrator_instances:
            return await ctx.send("You cannot set this channel as the registration channel because it is already being used as a registration channel.")

        if ctx.guild.channels.exists('id', reg_channel_id):
            return await ctx.send("The registration channel you provided was invalid.")

        self.bot.generator_instances[ctx.channel.id].setup(reg_channel_id, sheets_id, self_rating)
        self.bot.registrator_instances[reg_channel_id] = RegChannel(self.bot, ctx, registrator=Registrator())
        self.bot.registrator_instances[reg_channel_id].setup(ctx.channel.id, sheets_id)
        
        await ctx.send(f"I am now watching registrations in <#{reg_channel_id}>.")

    @commands.command(aliases=['endreg', 'closereg', 'stopreg'])
    async def close(self, ctx: commands.Context):
        '''
        Closes the registration.

        ''' 
        reg_channel_id = self.bot.generator_instances[ctx.channel.id].get_reg_channel()
        mes = self.bot.registrator_instances[reg_channel_id].close_reg()
        await ctx.send(mes)

    @commands.command(aliases=['initialize', 'init', 'create', 'begin'])
    async def start(self, ctx: commands.Context):
        '''
        Load player registrations and initialize the tournament.
        '''
        mes = self.bot.generator_instances[ctx.channel.id].start_tournament()
        await ctx.send(mes)
    
    @commands.command(aliases=['a', 'adv'])
    async def advance(self, ctx: commands.Context, *, players_arg):
        '''
        Advance a group of players to the next round.
        '''
        #TODO: process different player args (have to split by newlines or another special character)
        players = list()
        mes = self.bot.generator_instances[ctx.channel.id].advance_players(players)
        await ctx.send(mes)
    
    @advance.error
    async def advance_error(self, ctx: commands.Context, error):
        self.set_instance(ctx)
        if await self.check_callable("advance"): return

        if isinstance(error, commands.MissingRequiredArgument):
            await self.send_temp_messages(ctx, f"Usage: `{ctx.prefix}advance [player, ...]")
    
    @commands.command(aliases=['ua', 'unadv'])
    async def unadvance(self, ctx: commands.Context, *, players_arg):
        '''
        Unadvance a group of players from the next round advanced pool.
        '''
        #TODO: process different player args (have to split by newlines or another special character)
        players = list()
        mes = self.bot.generator_instances[ctx.channel.id].unadvance_players(players)
        await ctx.send(mes)
    
    @unadvance.error
    async def unadvance_error(self, ctx: commands.Context, error):
        self.set_instance(ctx)
        if await self.check_callable("unadvance"): return

        if isinstance(error, commands.MissingRequiredArgument):
            await self.send_temp_messages(ctx, f"Usage: `{ctx.prefix}unadvance [player, ...]")
    
    @commands.command(aliases=['increment', 'next'])
    async def nextround(self, ctx: commands.Context):
        '''
        Move on to the next round.
        '''
        mes = self.bot.generator_instances[ctx.channel.id].next_round()
        await ctx.send(mes)
    
    @commands.command(aliases=['rs', 'roundstatus'])
    async def status(self, ctx: commands.Context):
        '''
        Get the status (matchups that have finished and matchups that are still in progress) of the current round.
        '''
        pass

    @commands.command(aliases=['rr', 'roundresults', 'res'])
    async def results(self, ctx: commands.Context, round = -1):
        '''
        Get the results of a specific round (all matchups and winners of each matchup).
        '''
        pass

def setup(bot):
    bot.add_cog(Generation(bot))