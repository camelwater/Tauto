
from discord.ext import commands
from classes.registrator import Registrator
from classes.generator import Generator
import bot
from classes.Player import Player
import datetime

class RegChannel:

    def __init__(self, bot: bot.TournamentBOT, ctx: commands.Context):
        self.bot = bot
        self.prefix = ctx.prefix
        
        self.registrator = None
        self.open = None

    def setup(self, gen_channel_id, sheets_id, use_rating, registrator=None):
        self.gen_channel = gen_channel_id
        self.sheets_id = sheets_id
        self.use_rating = use_rating
        self.registrator = registrator if registrator else Registrator(sheets_id, use_rating=use_rating)
        self.open = True
    
    def register_player(self, user_id: int, name: str, rating: int = None, force=False):
        return self.registrator.add_registration([str(user_id), name, str(rating)], force=force)
    
    def drop_player(self, user_id: int):
        return self.registrator.remove_registration(user_id)
    
    def close_reg(self):
        self.open = False
        return "Registrations are now closed."
    
    def load_registrations(self):
        '''
        Load player registrations from registration sheet to feed to Generators.
        '''
        return self.registrator.load_registrations()
    
    def update_round_results(self, results):
        '''
        Updates the results sheet with a round's results.
        '''
        self.registrator.add_round_results(results)
    
    def cleanup_reg(self):
        self.registrator.reg_sheet = None
    
    def is_closed(self):
        return not self.open
    
    def using_rating(self):
        return self.use_rating
    
    def set_reg(self, registrator):
        self.registrator = registrator
    
    def get_reg(self):
        return self.registrator
    
    def get_gen_channel(self):
        return self.gen_channel
    

class GenChannel:

    def __init__(self, bot: bot.TournamentBOT, ctx, generator=None):
        self.bot = bot
        self.ctx = ctx
        self.prefix = ctx.prefix
        self.active = False
        self.last_active = None
        self.reg_channel = None
        self.skip_reg = False

        self.generator = generator

    def setup(self, reg_channel_id, sheets_id, self_rating, is_open, is_random):
        self.reg_channel = reg_channel_id #registration channel associated with this generation channel
        self.use_ratings = self_rating
        self.sheets_id = sheets_id
        self.open = is_open
        self.random = is_random
    
    def skip_reg_setup(self, sheets_id, self_rating, is_open, is_random):
        self.reg_channel = 0
        self.skip_reg = True
        self.use_rating = self_rating
        self.sheets_id = sheets_id
        self.open = is_open
        self.random = is_random
    
    def set_gen(self, generator):
        self.generator = generator
    
    def start_tournament(self):
        if self.skip_reg:
            self.reg_instance = RegChannel(self.bot, self.ctx)
            self.reg_instance.setup(0, self.sheets_id, self.use_rating)
            player_list = self.reg_instance.load_registrations()
            player_list = list(map(lambda l: Player(int(l[0]), None if l[1].lower()=="none" else int(l[1]), l[2], None if l[3].lower()=="none" else int(l[3])), player_list)) # convert lists into player objects

        else:
            registrator_instance = self.bot.registrator_instances[self.reg_channel]
            player_list = registrator_instance.load_registrations()
            player_list = list(map(lambda l: Player(int(l[0]), None if l[1].lower()=="none" else int(l[1]), l[2], None if l[3].lower()=="none" else int(l[3])), player_list)) # convert lists into player objects
            # self.bot.registrator_instances.pop(self.reg_channel) #remove registrator instance now that we are done using it
            registrator_instance.cleanup_reg()

        self.generator = Generator(player_list, is_open=self.open, random=self.random)
        ret = self.generator.start()
        
        self.active = True
        return ret
    
    def advance_players(self, players):
        if self.generator.is_final():
            return self.advance_winner(players)
        
        return self.generator.advance(players)
    
    def unadvance_players(self, players):
        return self.generator.unadvance(players)
        
    def advance_winner(self, players):
        if len(players)>1:
            return "You cannot have more than one winner."

        self.last_active = datetime.datetime.now()   
        ret = self.generator.advance_winner(players)
        return ret + f"\n`{self.prefix}finish` to finalize the tournament's results."
    
    def next_round(self):
        if self.generator.winner:
            self.end_tournament()

        round_finished, round, status_str, cur_round_status = self.generator.round_finished()
        if not round_finished:
            return f"The current round ({round}) is still in progress. " + status_str, round, cur_round_status
        
        registration_instance = self.bot.registrator_instances[self.reg_channel] if not self.skip_reg else self.reg_instance
        ret = self.generator.next_round()
        registration_instance.update_round_results(self.generator.get_round_results(local_call=True))
        return ret
    
    def round_results(self, round):
        return self.generator.get_round_results(round)
    
    def round_status(self):
        return self.generator.current_round_status()
    
    def end_tournament(self):
        self.generator.determine_winner()
        registration_instance = self.bot.registrator_instances[self.reg_channel] if not self.skip_reg else self.reg_instance
        registration_instance.update_round_results(self.generator.get_round_results(local_call=True))

    def is_active(self):
        return self.active
    
    def is_open(self):
        return self.reg_channel is not None
    
    def reg_open(self):
        if self.skip_reg:
            return False
        return self.bot.registrator_instances[self.reg_channel].open
    
    def is_finished(self):
        if self.generator is None: return False
        return self.generator.winner is not None
    
    def get_winner(self):
        return self.generator.winner

    def get_ctx(self):
        return self.ctx
    
    def get_gen(self):
        return self.generator
    
    def get_reg_channel(self):
        return self.reg_channel