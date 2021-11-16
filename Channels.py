
from registrator import Registrator
from generator import Generator

class RegChannel:

    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        
        self.registrator = None

    def setup(self, gen_channel_id, sheets_id, use_rating):
        self.gen_channel = gen_channel_id
        self.sheets_id = sheets_id
        self.use_rating = use_rating
        self.registrator = Registrator(sheets_id, use_rating=use_rating)
        self.open = True
    
    def register_player(self, user_id: int, name: str, rating: int = None):
        return self.registrator.add_registration(user_id, name, rating)
    
    def drop_player(self, user_id: int):
        return self.registrator.remove_registration(user_id)
    
    def close_reg(self):
        self.open = False
        return "Registrations are now closed."
    
    def load_registrations(self):
        '''
        Load player registrations from registration sheet to feed to Generators.
        '''
        pass
    
    def is_closed(self):
        return not self.open
    
    def get_ctx(self):
        return self.ctx
    
    def set_reg(self, registrator):
        self.registrator = registrator
    
    def get_reg(self):
        return self.registrator
    
    def get_gen_channel(self):
        return self.gen_channel
    

class GenChannel:

    def __init__(self, bot, ctx, generator=None):
        self.bot = bot
        self.ctx = ctx

        self.generator = generator

    
    def setup(self, reg_channel_id, sheets_id, self_rating, is_open, is_random):
        self.reg_channel = reg_channel_id #registration channel associated with this generation channel
        self.use_ratings = self_rating
        self.sheets_id = sheets_id
        self.open = is_open
        self.random = is_random
    
    def set_gen(self, generator):
        self.generator = generator
    
    def start_tournament(self):
        registrator_instance = self.bot.registrator_instances[self.reg_channel]
        player_list = registrator_instance.load_registrations()
        self.generator = Generator(player_list, is_open=self.open, random=self.random)
        return self.generator.start()

    def get_ctx(self):
        return self.ctx
    
    def get_gen(self):
        return self.generator
    
    def get_reg_channel(self):
        return self.reg_channel