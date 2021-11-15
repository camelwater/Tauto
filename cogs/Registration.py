import discord
from discord.ext import commands
from Errors import *

class Registration(commands.Cog):
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
        
    async def check_instance(self, ctx: commands.Context):
        '''
        Add a GenChannel instance into the generator_instances dictionary if it isn't present.
        '''

        channel_id = ctx.channel.id
        
        if channel_id in self.bot.registrator_instances: 
            self.bot.registrator_instances[channel_id].prefix = ctx.prefix
            return

        raise RegChannelSetupError

    async def cog_before_invoke(self, ctx):
        self.check_instance(ctx)
    
    @commands.command(aliases=['r', 'c', 'can', 'reg', 'join', 'j'])
    async def register(self, ctx: commands.Context, name: str, rating: str = None):
        '''
        Register for the tournament.
        '''
        if rating and not rating.isnumeric():
            await ctx.message.add_reaction(":x:")
            return await self.send_messages(ctx, "The `rating` parameter must be numeric.")

        reaction, mes = self.bot.registrator_instances[ctx.channel.id].register_player(ctx.message.author.id, name, int(rating))
        ctx.message.add_reaction(reaction)
        await ctx.send(mes)
    
    @register.error
    async def register_error(self, ctx: commands.Context, error):
        self.check_instance(ctx)
        if isinstance(error, commands.MissingRequiredArgument):
            if len(error.args) == 2:
                ctx.message.add_reaction(":x:")
                await self.send_messages(ctx, f"Usage: `{ctx.prefix}register [name] {'[rating]' if self.bot.registrator_instances[ctx.channel.id].using_rating() else '(rating)'}`")
            else:
                ctx.message.add_reaction(":x:")
                await self.send_messages(ctx, f"You must register in this format: `{ctx.prefix}register [name] {'[rating]' if self.bot.registrator_instances[ctx.channel.id].using_rating() else '(rating)'}`")

    @commands.command(aliases=['unregister', 'd', 'q', 'quit', 'leave', 'unreg', 'l'])
    async def drop(self, ctx: commands.Context):
        '''
        Drop from the tournament.
        '''

        reaction, mes = self.bot.registrator_instances[ctx.channel.id].drop_player(ctx.message.author.id)
        ctx.message.add_reaction(reaction)
        await ctx.send(mes)

    @commands.command(aliases=['end', 'endreg', 'stopreg', 'closereg'])
    async def close(self, ctx: commands.Context):
        '''
        Close player registrations.
        '''
        await ctx.send(self.bot.registrator_instances.close_reg())

def setup(bot):
    bot.add_cog(Registration(bot))