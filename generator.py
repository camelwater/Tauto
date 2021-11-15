import copy
import random as rd
import math
import utils.gen_utils as gen_utils
from Player import Player
from typing import List, Dict, Set

class Generator:
    def __init__(self, players: Set[Player] = list(), is_open = True, random=False): #random only applies to open tournaments (bracketed tournaments will always be randomized, not seeded)
        self.players = players
        self.remaining_players = copy.copy(self.players)
        self.out_players = set()
        self.round_groupings = list() #list of every round's groupings (made from generate_round)
        
        self.total_rounds = math.floor(math.log2(len(players)))
        self.round = 0

        self.round_advancements = [[]] #list of every round's advancements (winners of round)

        self.is_open = is_open
        self.random = random

        self.has_prelim = not math.log2(len(self.players)).is_integer()
        self.round_after_prelim = False
        self.prelim_round_matches = None
        self.byes = None
    
    def start(self):
        '''
        initialize tournament with first round 

        for single-elimination tournaments, all byes are resolved in a preliminary round, where
        n unranked/unrated players (where n = next power of 2 after p - p and where p = # players) will play for spots in the first round

        in this case, the tournament is initialized with this prelim round and then will advance to the first round
        
        '''
        if self.has_prelim: #tournament needs a prelim round
            return self.generate_prelim()

        return self.generate_round(self.remaining_players)
    
    def generate_prelim(self):
        players = sorted(self.remaining_players, key=lambda player: player.getRating(), reverse=True)
        num_byes = gen_utils.next_power2(len(self.remaining_players)) - len(self.remaining_players)
        byes = players[:num_byes]
        prelim_players = players[num_byes:]
        prelim_matches = self.generate_round(prelim_players, prelim = True)
        self.round_after_prelim = True
        self.byes = byes

        return (prelim_matches, byes)
          
    # def next_round(self, advanced = None):
    #     '''
    #     initialize tournament's next round
    #     '''
    #     return self.generate_round(advanced)
    
    def next_round(self):
        '''
        initialize next round's matchups
        '''
        next_round = self.generate_round(self.get_last_advancements())
        self.round_advancements.append([])
        return next_round

    def advance(self, advanced: list):
        advanced = list(self.process_advancements(advanced))
        self.round_advancements[-1].extend(advanced)
        
    def get_last_advancements(self):
        return self.round_advancements[-1]
    
    def get_current_groupings(self):
        try:
            return self.round_groupings[-1]
        except IndexError:
            return self.prelim_round_matches

    def round_finished(self):
        # print(self.get_last_advancements())
        # print(self.get_current_groupings())
        return len(self.get_last_advancements()) == len(self.get_current_groupings())

    def generate_round(self, advanced, prelim = False) -> List[List[Player]]:
        '''
        generate pairs (opponents) from advanced players
        '''
        if prelim:
            self.remaining_players = advanced
            next_round_matches = self.random_generation()
            self.prelim_round_matches = next_round_matches
            return next_round_matches

        self.remaining_players = advanced
        if self.round_after_prelim: # after advancing players from prelim round, add the byes to next round pool
            self.round_after_prelim = False
            self.remaining_players.extend(self.byes)

        if self.is_open:
            if self.random:
                next_round_matches = self.random_generation()
            else:
                next_round_matches = self.seeded_generation()

        else:
            next_round_matches = self.random_generation()
        
        self.round_groupings.append(next_round_matches)
        
        return next_round_matches
    
    def seeded_generation(self):
        '''
        generate matches by seeds

        number of remaining participants must be base 2

        ex.
        8 -> 1v8, 2v7, 3v6, etc.
        '''
        middle = int(len(self.remaining_players)/2)
        remaining_front = sorted(self.remaining_players, key=lambda player: player.getRating(), reverse=True)
        remaining_back = remaining_front[::-1][:middle]
        remaining_front = remaining_front[:middle]
        matches = list()
        for f, b in zip(remaining_front, remaining_back):
            match = [f, b]
            rd.shuffle(match)
            matches.append(match)
        
        return matches
        
    def random_generation(self):
        remaining = copy.copy(self.remaining_players)
        rd.shuffle(remaining)
        next_round_matches = gen_utils.group2(remaining)
        return next_round_matches
            
    def process_advancements(self, advanced):
        return set([player for player in self.remaining_players if gen_utils.is_advanced(player, advanced)])

    # def current_round_status(self):
    #     '''
    #     get the status of the current round in progress.

    #     shows which players from matchups have already been advanced, and which matchups are still in progress.
    #     '''

    def get_round_results(self, round):
        #TODO: need to go through round groupings and cross examine each matchup to see which player 
        # advanced out of the match (by looking through self.round_advancements)

        if round == -1: round == len(self.round_groupings) #get last round's results
        if round == 0 and self.prelim_round_matches: #get prelim round (either manually called or automatically since last round was prelim)
            pass
    
    def get_tournament_results(self):
        '''
        get results of entire tournament, including each round's results and overall stats of the tournament
        ie. best player, average rating, etc. (can determine which stats to show)
        '''
        pass

    def current_round_status(self, round_num = -1, prelim = False):
        if round_num<0: round_num = len(self.round_groupings)
        if prelim or (round_num == 0 and self.prelim_round_matches): #last round was prelim
            ret = f"PRELIM ROUND MATCHES:\n"
            for i, match in enumerate(self.prelim_round_matches):
                ret+= f"Match {i+1}: {match[0]} (W) vs. {match[1]} (B)\n"
            return ret

        ret = f"ROUND {round_num} MATCHES:\n"
        round_num = round_num-1
        for i, match in enumerate(self.round_groupings[round_num]):
            if len(match)<2: #bye round
                ret+= f"Match {i+1} (BYE): {match[0]}"
            else:
                ret+= f"Match {i+1}: {match[0]} (W) vs. {match[1]} (B)\n"
        return ret

    def overall_status(self):
        ret = "TOURNAMENT MATCHES:\n"
        
        if self.prelim_round_matches:
            ret+=self.current_round_status(prelim=True)

        for num, round in enumerate(self.round_groupings):
            ret+="\n"+self.current_round_status(num+1)
        return ret

            