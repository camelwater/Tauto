
class RegChannel:

    def __init__(self, bot, ctx, registrator=None):
        self.bot = bot
        self.ctx = ctx

        self.registrator = registrator

    def setup(self, gen_channel_id, sheets_id, use_rating):
        self.gen_channel = gen_channel_id
        self.sheets_id = sheets_id
        self.registrator.sheets_id = sheets_id
        self.registrator.use_rating = use_rating
        self.use_rating = use_rating
    
    def register_player(self, user_id: int, name: str, rating: int = None):
        return self.registrator.register(user_id, name, rating)
    
    def drop_player(self, user_id: int):
        return self.registrator.drop(user_id)
    
    def close_reg(self):
        return self.registrator.close()
    
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
    
    def setup(self, reg_channel_id, sheets_id, self_rating):
        self.reg_channel = reg_channel_id #registration channel associated with this generation channel
        self.use_ratings = self_rating
        self.sheets_id = sheets_id
    
    def set_gen(self, generator):
        self.generator = generator

    def get_ctx(self):
        return self.ctx
    
    def get_gen(self):
        return self.generator
    
    def get_reg_channel(self):
        return self.reg_channel