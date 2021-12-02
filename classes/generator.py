from abc import abstractmethod
import copy
import random as rd
import math
import utils.gen_utils as gen_utils
import classes.Player as Player
from typing import List, Dict, Set

class Generator:
    def __init__(self, players: List[Player.Player] = list(), seeding=True, bracket=True): 
        self.players = players
        self.remaining_players = copy.copy(self.players)

        self.total_rounds = math.floor(math.log2(len(players)))
        self.round = 0

        self.seeding = seeding #if seeding is False: matches are randomly generated (no seeds/ranking)
        self.bracket = bracket #if bracket is True: bracket is created and matches are not redrawn every round, if bracket is False: every round requires a redraw

        self.has_prelim = not math.log2(len(self.players)).is_integer()
        self.round_after_prelim = False
        self.byes = None

        self.winner = None

        
    @abstractmethod
    def start(self):
        '''
        initialize tournament with first round 

        for single-elimination tournaments, all byes are resolved in a preliminary round, where
        n unranked/unrated players (where n = next power of 2 after p - p and where p = # players) will play for spots in the first round

        in this case, the tournament is initialized with this prelim round and then will advance to the first round
        
        '''
        pass
    
    @abstractmethod
    def generate_round(self, advanced, prelim=False) -> List[List[Player.Player]]:
        '''
        generate pairs (opponents) from advanced players
        '''
        pass
    
    @abstractmethod
    def next_round(self):
        '''
        initialize next round's matchups
        '''
        pass

    @abstractmethod
    def advance(self, advanced: list):
        pass
    
    @abstractmethod
    def unadvance(self, players: list):
        pass
    
    @abstractmethod
    def advance_winner(self, player):
        pass
    
    def determine_winner(self):
        self.round_advancements[self.round].append(self.winner)

    def get_last_advancements(self):
        return list(self.round_advancements.values())[-1]
    
    def get_current_groupings(self):
        return list(self.round_groupings.values())[-1]
    
    @abstractmethod
    def is_final(self):
        '''
        Whether the tournament is in the final round (1v1).
        '''
        pass

    @abstractmethod
    def round_finished(self):
        pass

    @abstractmethod
    def bracketed_generation(self):
        '''
        generate next round matches through bracket
        '''
        pass

    @abstractmethod
    def seeded_generation(self):
        '''
        generate matches by seeds

        number of remaining participants must be base 2

        ex.
        8 -> 1v8, 2v7, 3v6, 4v5
        '''
        pass
    
    @abstractmethod
    def random_generation(self):
        pass
    
    @abstractmethod
    def process_winner(self, o_player):
        pass
    
    @abstractmethod
    def process_unadvancements(self, unadvanced):
        pass

    @abstractmethod
    def process_advancements(self, advanced):
        pass

    @abstractmethod
    def matchups_to_str(self, matchups: List[List[Player.Player]]):
        '''
        Convert round matchups (list of lists) to a string.
        '''
        pass

    @abstractmethod
    def get_round_results(self, round=-1, local_call=False):
        pass
    
    @abstractmethod
    def __round_results(self, round, local_call):
        pass

    @abstractmethod         
    def get_tournament_results(self):
        '''
        get results of entire tournament, including each round's results and overall stats of the tournament
        ie. best player, average rating, etc. (can determine which stats to show)
        '''
        pass
    
    @abstractmethod
    def current_round_status(self):
        '''
        get the status of the current round in progress.

        shows which players from matchups have already been advanced, and which matchups are still in progress.
        '''
        pass    