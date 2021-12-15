import discord
import utils.discord_utils as discord_utils
# from discord.ext import commands
# from dotenv import dotenv_values

# creds = dotenv_values('.env.testing')
# KEY = creds['KEY']

class DropDownMenu(discord.ui.Select['TournamentFormatView']):
    def __init__(self):
        options = [discord.SelectOption(label="Single Elimination"), 
                discord.SelectOption(label='Double Elimination'), discord.SelectOption(label="Champions League")]
        super().__init__(placeholder="Single Elimination", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        view=self.view
        view.selected = interaction.data.get('values')[0]
        # view.enable_done_button()
        # await interaction.response.edit_message(view=view)
        
class DoneButton(discord.ui.Button['TournamentFormatView']):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label='Open')
    
    async def callback(self, interaction: discord.Interaction):
        for child in self.view.children:
            child.disabled = True
        self.view.stop()
        await self.view.gen_channel.set_tournament(discord_utils.convert_str_to_tournament(self.view.selected))
        content = f"`{self.view.selected}` format selected."
        # await self.view.gen_channel.ctx.send(content)
        await interaction.response.edit_message(content=content, view=self.view)

class TournamentFormatView(discord.ui.View):
    def __init__(self, gen_channel):
        super().__init__()
        self.selected = "Single Elimination"
        self.gen_channel = gen_channel
        self.add_item(DropDownMenu())
        self.add_item(DoneButton())
    
    # def enable_done_button(self):
    #     self.children[-1].disabled=False # index of button



# bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'))

# @bot.command(name='try')
# async def _try(ctx: commands.Context):
#     await ctx.send("Select tournament format:", view=TournamentFormatView())

#     bot.run(KEY)