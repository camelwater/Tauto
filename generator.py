import copy
import random as rd
import math
import Utils
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
        self.is_open = is_open
        self.random = random
        self.first_after_prelim = False
        self.prelim_round_matches = None
        self.byes = None
    
    def start(self):
        '''
        initialize tournament with first round 

        for single-elimination tournaments, all byes are resolved in a preliminary round, where
        n unranked/unrated players (where n = next power of 2 after p - p and where p = # players) will play for spots in the first round

        in this case, the tournament is initialized with this prelim round and then will advance to the first round
        
        '''
        if not math.log2(len(self.players)).is_integer(): #tournament needs a prelim round
            return self.generate_prelim()

        return self.generate_round(first = True)
    
    def generate_prelim(self):
        players = sorted(self.remaining_players, key=lambda player: player.getRating(), reverse=True)
        num_byes = Utils.next_power2(len(self.remaining_players)) - len(self.remaining_players)
        print(num_byes)
        byes = players[:num_byes]
        prelim_players = players[num_byes:]
        prelim_matches = self.generate_round(prelim_players, prelim = True)
        self.first_after_prelim = True
        self.byes = byes

        return (prelim_matches, byes)
          
    def next_round(self, advanced = None):
        '''
        initialize tournament's next round
        '''
        return self.generate_round(advanced)
    
    def generate_round(self, advanced = None, first = False, prelim = False) -> List[List[Player]]:
        '''
        generate pairs (opponents) from advanced players
        '''
        if prelim:
            self.remaining_players = advanced
            next_round_matches = self.random_generation()
            self.prelim_round_matches = next_round_matches
            return next_round_matches

        self.remaining_players = list(self.process_advancements(advanced)) if not first else self.remaining_players
        if self.first_after_prelim: # after advancing players from prelim round, add the byes to next round pool
            self.first_after_prelim = False
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
        next_round_matches = Utils.group2(remaining)
        return next_round_matches
            
    def process_advancements(self, advanced):
        return set([player for player in self.remaining_players if Utils.is_advanced(player, advanced)])

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

            