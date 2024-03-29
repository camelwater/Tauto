import discord
from discord.ext import commands
from classes.Exceptions import *
import bot

class Registration(commands.Cog):
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
        if ctx.command not in self.bot.get_cog('Registration').get_commands(): return
        # await self.check_instance(ctx)

    async def check_instance(self, ctx: commands.Context):
        '''
        '''
        channel_id = ctx.channel.id
        
        if channel_id in self.bot.registrator_instances: 
            # self.bot.registrator_instances[channel_id].ctx = ctx
            self.bot.registrator_instances[channel_id].prefix = ctx.prefix
            return
        
        await ctx.send(f"You have not set up this channel to be a registration channel. If you'd like to set this channel as a registration channel, use `{ctx.prefix}open`.", delete_after=15)
        raise RegChannelSetupError

    async def cog_before_invoke(self, ctx):
        await self.check_instance(ctx)
    
    @commands.command(aliases=['r', 'c', 'can', 'reg', 'join', 'j'])
    async def register(self, ctx: commands.Context, name: str, rating: str = None):
        '''
        Register for the tournament.
        '''
        if self.bot.registrator_instances[ctx.channel.id].is_closed():
            return 

        if rating and not rating.isnumeric():
            await ctx.message.add_reaction("❌")
            return await self.send_messages(ctx, "The `rating` parameter must be numeric.")

        reaction, mes = self.bot.registrator_instances[ctx.channel.id].register_player(ctx.message.author.id, name, rating)
        await ctx.message.add_reaction(reaction)
        if mes: await ctx.send(mes)
    
    @register.error
    async def register_error(self, ctx: commands.Context, error):
        await self.check_instance(ctx)
        if self.bot.registrator_instances[ctx.channel.id].is_closed():
            return 

        if isinstance(error, commands.MissingRequiredArgument):
            if len(error.args) == 2:
                await ctx.message.add_reaction("❌")
                await self.send_messages(ctx, f"Usage: `{ctx.prefix}register [name] {'[rating]' if self.bot.registrator_instances[ctx.channel.id].using_rating() else '(rating)'}`")
            else:
                await ctx.message.add_reaction("❌")
                await self.send_messages(ctx, f"You must register in this format: `{ctx.prefix}register [name] {'[rating]' if self.bot.registrator_instances[ctx.channel.id].using_rating() else '(rating)'}`")

    @commands.command(aliases=['mreg', 'areg', 'forcereg', 'freg', 'fr'])
    @commands.has_guild_permissions(administrator=True)
    async def forceregister(self, ctx: commands.Context, name: str, rating: str = None):
        if rating and not rating.isnumeric():
            await ctx.message.add_reaction("❌")
            return await self.send_messages(ctx, "The `rating` parameter must be numeric.")

        reaction, mes = self.bot.registrator_instances[ctx.channel.id].register_player(None, name, rating, force=True)
        await ctx.message.add_reaction(reaction)
        if mes: await ctx.send(mes)


    @commands.command(aliases=['unregister', 'd', 'q', 'quit', 'leave', 'unreg', 'l'])
    async def drop(self, ctx: commands.Context):
        '''
        Drop from the tournament.
        '''
        if self.bot.registrator_instances[ctx.channel.id].is_closed():
            return 
        reaction, mes = self.bot.registrator_instances[ctx.channel.id].drop_player(ctx.message.author.id)
        await ctx.message.add_reaction(reaction)
        if mes:
            await ctx.send(mes)

def setup(bot):
    bot.add_cog(Registration(bot))