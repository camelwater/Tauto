import copy
import classes.generator as generator

class ChampionsLeague(generator.Generator):
    def __init__(self, players = list()):
        self.players = players
        self.remaining_players = copy.copy(players)