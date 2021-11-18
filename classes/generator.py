import copy
import random as rd
import math
import utils.gen_utils as gen_utils
from classes.Player import Player
from typing import List, Dict, Set
import utils.discord_utils as discord_utils
from collections import defaultdict

class Generator:
    def __init__(self, players: Set[Player] = list(), is_open = True, random=False): #random only applies to open tournaments (bracketed tournaments will always be randomized, not seeded)
        self.players = players
        self.remaining_players = copy.copy(self.players)
        self.out_players = set()
        self.round_groupings = defaultdict(list) #dict of every round's groupings (made from generate_round)
        
        self.total_rounds = math.floor(math.log2(len(players)))
        self.round = 0

        self.round_advancements = defaultdict(list) #dict of every round's advancements (winners of round)
        self.current_advancements = []

        self.is_open = is_open
        self.random = random

        self.has_prelim = not math.log2(len(self.players)).is_integer()
        self.round_after_prelim = False
        self.byes = None

        self.winner = None
    
    def start(self):
        '''
        initialize tournament with first round 

        for single-elimination tournaments, all byes are resolved in a preliminary round, where
        n unranked/unrated players (where n = next power of 2 after p - p and where p = # players) will play for spots in the first round

        in this case, the tournament is initialized with this prelim round and then will advance to the first round
        
        '''
        if self.has_prelim: #tournament needs a prelim round
            return "Tournament started. Preliminary Round generation complete.", "prelim", self.matchups_to_str(self.generate_prelim())

        self.round+=1
        return "Tournament started. Round 1 generation complete.", 1, self.matchups_to_str(self.generate_round(self.remaining_players))
    
    def generate_prelim(self):
        players = sorted(self.remaining_players, key=lambda player: player.getRating(), reverse=True)
        num_byes = gen_utils.next_power2(len(self.remaining_players)) - len(self.remaining_players)
        byes = players[:num_byes]
        prelim_players = players[num_byes:]
        prelim_matches = self.generate_round(prelim_players, prelim = True)
        self.round_after_prelim = True
        self.byes = byes

        return (prelim_matches, byes)
    
    def next_round(self):
        '''
        initialize next round's matchups
        '''
        self.round_advancements[self.round].extend(self.current_advancements)
        self.round+=1
        next_round = self.generate_round(self.current_advancements)
        self.current_advancements = []

        return f"Round {self.round} generation complete.", self.round, self.matchups_to_str(next_round)

    def advance(self, advanced: list):
        advanced = list(self.process_advancements(advanced))
        self.current_advancements.extend(advanced)
        return f"{len(advanced)} players advanced. {len(self.current_advancements)}/{len(self.get_current_groupings())} players advanced from {'preliminary round' if self.round==0 else f'round {self.round}'}."
    
    def unadvance(self, players: list):
        players = list(self.process_advancements(players))
        for player in players:
            try:
                self.current_advancements.remove(player)
            except:
                pass
        return f"{len(players)} players unadvanced. {len(self.current_advancements)}/{len(self.get_current_groupings())} players advanced from {'preliminary round' if self.round==0 else f'round {self.round}'}."

    def determine_winner(self, players):
        winner = list(self.process_advancements(players))[0]
        self.round_advancements[self.round].append(winner)
        # self.round_advancements[-1].append(winner)
        self.winner = winner

        return f"Final round finished. {self.winner.get_displayName()} is the winner."

    def get_last_advancements(self):
        return list(self.round_advancements.values())[-1]
    
    def get_current_groupings(self):
        return list(self.round_groupings.values())[-1]
        
    def is_final(self):
        '''
        Whether the tournament is in the final round (1v1).
        '''
        return self.round>0 and len(self.get_current_groupings()) == 1

    def round_finished(self):
        return (len(self.current_advancements) == len(self.get_current_groupings()), 
                    f"{len(self.current_advancements)}/{len(self.get_current_groupings())} players advanced.")

    def generate_round(self, advanced, prelim = False) -> List[List[Player]]:
        '''
        generate pairs (opponents) from advanced players
        '''

        self.remaining_players = advanced
        if self.round_after_prelim: # after advancing players from prelim round, add the byes to next round pool
            self.round_after_prelim = False
            self.remaining_players.extend(self.byes)

        if self.is_open:
            next_round_matches = self.random_generation() if self.random else self.seeded_generation()
        else:
            next_round_matches = self.random_generation()
        
        self.round_groupings[self.round] = next_round_matches
        
        return next_round_matches
    
    def seeded_generation(self):
        '''
        generate matches by seeds

        number of remaining participants must be base 2

        ex.
        8 -> 1v8, 2v7, 3v6, 4v5
        '''
        middle = int(len(self.remaining_players)/2)
        remaining_front = sorted(self.remaining_players, key=lambda player: player.getRating(), reverse=True)
        remaining_back = remaining_front[::-1][:middle]
        remaining_front = remaining_front[:middle]
        matches = list()
        for f, b in zip(remaining_front, remaining_back):
            rand_num = rd.randint(0,1)
            match = [f, b] if rand_num == 0 else [b, f]
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
    def matchups_to_str(self, matchups: List[List[Player]]):
        '''
        Convert round matchups (list of lists) to a string.
        '''
        cur_round = "Preliminary Round" if self.round == 0 else f"Round {self.round}"
        ret = cur_round + " Matchups\n\n"

        if isinstance(matchups, tuple): #prelim round
            matchups, byes = matchups[0], matchups[1]

            ret+="Byes:\n"
            for b in byes:
                ret+=' - '+str(b)+'\n'
            ret+="\n"

        for i, match in enumerate(matchups):
            ret+=f"Match {i+1}: {discord_utils.disc_clean(match[0].get_full_display())} {{A}} vs. {discord_utils.disc_clean(match[1].get_full_display())} {{DA}}\n"
        
        return ret

    def get_round_results(self, round=-1, local_call=False):
        if round == -1: round = list(self.round_advancements.keys())[-1] #get last round's results

        try:
            assert(round in self.round_advancements)
        except AssertionError:
            return f"{round} is an invalid round: it must be from {list(self.round_advancements.keys())[0]}-{list(self.round_advancements.keys())[-1]}, or \"prelim\" if there was a preliminary round."

        round_data = self.__round_results(round)
        return ("Prelim Round" if round == 0 else f"Round {round}"), round_data
        
    def __round_results(self, round):
       
        matchups = []
        for num, match in enumerate(self.round_groupings[round]):  
            player1 = match[0].get_full_display()
            player2 = match[1].get_full_display()
            match = [num+1, player1, player2] if player1 in self.round_advancements[round] else [num+1, player2, player1]

            matchups.append(match)
        
        return matchups

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

            