from collections import defaultdict
import copy
from typing import Dict, List
import classes.Player as Player
import classes.generator as generator

class ChampionsLeague(generator.Generator):
    def __init__(self, players = list(), seeding=True, bracket=True, num_groups=None, group_size=None, knockout_size=16):
        super().__init__(players, seeding=seeding, bracket=bracket)
        self.num_groups = num_groups
        self.group_size = group_size
        self.knockout_size = knockout_size #how many players will advance from group stages to knockout (must be base 2 number because I don't want to implement prelims)

        self.groups = defaultdict(list) #keys are group numbers
        self.group_advancements: Dict[int, List[Player.Player]] = defaultdict(list) #keys are group numbers

        self.knockout_round_groupings = defaultdict(list)
        self.knockout_round_advancements = defaultdict(list)

        self.current_advancements = list()

    def start(self):
        pass
    
