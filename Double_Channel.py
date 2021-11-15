
class DoubleChannel:
    '''
    This class acts as a bridge between Generators and Discord channels.
    A server can have multiple DoubleChannel instances and each instance is separate.

    There are two channels that it manages: the registration channel and the generation channel.

    The registration channel is where players register for the tournament, and the generation channel
    is where bot commands to manage the tournament automation is done. 
    '''

    def __init__(self, bot, ctx, generator, reg_channel, gen_channel):
        self.reg_channel = reg_channel
        self.gen_channel = gen_channel
        self.active = False

        self.bot = bot
        self.ctx = ctx
        self.generator = generator

        self.generator.channel = self

    def get_gen(self):
        return self.generator
    
    def get_ctx(self):
        return self.ctx

    def is_active(self):
        return self.active
    
    def get_reg_channel(self):
        return self.reg_channel
    
    def get_gen_channel(self):
        return self.gen_channel
    
        

