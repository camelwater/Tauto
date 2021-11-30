import copy
from random import seed
import classes.generator as generator

class DoubleElim(generator.Generator):
    def __init__(self, players = list(), seeding=True, bracket=True):
        super().__init__(players, seeding=seeding, bracket=bracket)
        self.winner_players = copy.copy(players) #winners bracket
        self.loser_players = copy.copy(players) #losers bracket

        self.winner_round_groups = []
        self.loser_round_groups = []
