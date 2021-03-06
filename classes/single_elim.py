import copy
import random as rd
import math
import utils.gen_utils as gen_utils
import classes.Player as Player
from typing import List, Dict, Set
import utils.discord_utils as discord_utils
from collections import defaultdict
import classes.generator as generator

class SingleElim(generator.Generator):
    def __init__(self, players: List[Player.Player] = list(), seeding=True, bracket=True): 
        super().__init__(players, seeding=seeding, bracket=bracket)

        self.round_groupings = defaultdict(list) #dict of every round's groupings (made from generate_round)
        self.round_advancements = defaultdict(list) #dict of every round's advancements (winners of round)
        self.current_advancements = list()
    
    def start(self):
        '''
        initialize tournament with first round 

        for single-elimination tournaments, all byes are resolved in a preliminary round, where
        n unranked/unrated players (where n = next power of 2 after p - p and where p = # players) will play for spots in the first round

        in this case, the tournament is initialized with this prelim round and then will advance to the first round
        
        '''
        if self.has_prelim: #tournament needs a prelim round
            return f"Tournament started. Seeding={self.seeding}, Bracket={self.bracket}. Preliminary Round generation complete.", "Prelim Round", self.matchups_to_str(self.generate_prelim())

        self.round+=1
        return f"Tournament started. Seeding={self.seeding}, Bracket={self.bracket}. Round 1 generation complete.", "Round 1", self.matchups_to_str(self.gen_first_round())
    
    def generate_prelim(self):
        if self.seeding:
            players = sorted(self.remaining_players, key=lambda player: player.getRating(), reverse=True)
        else:
            players = copy.copy(self.remaining_players)
            players.shuffle()

        num_byes = gen_utils.next_power2(len(players)) - len(players)
        byes = players[:num_byes]
        prelim_players = players[num_byes:]
        prelim_matches = self.generate_round(prelim_players, prelim=True)
        self.round_after_prelim = True
        self.byes = byes

        return (prelim_matches, byes)
    
    def gen_first_round(self):
        if self.seeding:
            players = sorted(self.remaining_players, key=lambda player: player.getRating(), reverse=True)
        else:
            players = copy.copy(self.remaining_players)
            players.shuffle()
        
        return self.generate_round(players)
    
    def generate_round(self, advanced, prelim=False) -> List[List[Player.Player]]:
        '''
        generate pairs (opponents) from advanced players
        '''

        self.remaining_players = advanced
        if self.round_after_prelim: # after advancing players from prelim round, add the byes to next round pool
            self.round_after_prelim = False
            self.remaining_players = self.byes + advanced #byes are order-wise in front of prelim advancements

        if self.bracket and not prelim:
            next_round_matches = self.bracketed_generation()
        else: #redraw every round 
            next_round_matches = self.seeded_generation() if self.seeding else self.random_generation()
        
        
        self.round_groupings[self.round] = next_round_matches
        
        return next_round_matches
    
    def next_round(self):
        '''
        initialize next round's matchups
        '''
        round_finished, round, status_str, cur_round_status = self.round_finished()
        if not round_finished:
            return round_finished, f"The current round ({round}) is still in progress. " + status_str, round+" status", cur_round_status

        self.current_advancements = gen_utils.get_bracket_order(self.current_advancements, self.get_current_groupings())
        self.round_advancements[self.round].extend(self.current_advancements)
        self.round+=1
        next_round = self.generate_round(self.current_advancements)
        self.current_advancements = []

        return (round_finished, f"Next round started. Round {self.round} ({gen_utils.get_round_name(len(self.remaining_players))}) generation complete.",
                f"Round {self.round} Matchups", self.matchups_to_str(next_round))

    def advance(self, advanced: list):
        players, errors = list(self.process_advancements(advanced))
        header_mes = f"{len(players)} players advanced. {len(self.current_advancements)}/{len(self.get_current_groupings())} players advanced from {'preliminary round' if self.round==0 else f'round {self.round}'}."
        if len(errors) == 0:
            return header_mes

        error_mes = f"\n\n{len(errors)} players could not be advanced:\n"
        for o_p, p, err in errors:
            error_mes+=f"`{o_p}`{f' ({p.getName()})' if p else ''}: {err}"
        
        return header_mes+error_mes
    
    def unadvance(self, players: list):
        num_players, errors = list(self.process_unadvancements(players))

        header_mes = f"{num_players} players unadvanced. {len(self.current_advancements)}/{len(self.get_current_groupings())} players advanced from {'preliminary round' if self.round==0 else f'round {self.round}'}."
        if len(errors) == 0:
            return header_mes
        
        error_mes = f"\n\n{len(errors)} players could not be unadvanced:\n"
        for o_p, p, err in errors:
            error_mes+=f"`{o_p}`{f' ({p.getName()})' if p else ''}: {err}"
        
        return header_mes+error_mes

    def advance_winner(self, player):
        player = player[0]
        winner, error = list(self.process_winner(player))
        if error is not None:
            o_p, p, mes = error
            return f"`{o_p}`{f' ({p.getName()})' if p else ''} {mes}."

        # self.round_advancements[self.round].append(winner)
        self.winner = winner

        return f"Final round finished. {self.winner.get_displayName()} is the winner."
    
    # def determine_winner(self):
    #     self.round_advancements[self.round].append(self.winner)

    # def get_last_advancements(self):
    #     return list(self.round_advancements.values())[-1]
    
    # def get_current_groupings(self):
    #     return list(self.round_groupings.values())[-1]
        
    def is_final(self):
        '''
        Whether the tournament is in the final round (1v1).
        '''
        return self.round>0 and len(self.get_current_groupings()) == 1

    def round_finished(self):
        return (len(self.current_advancements) == len(self.get_current_groupings()), "prelim round" if self.round==0 else f"round {self.round}",
                    f"{len(self.current_advancements)}/{len(self.get_current_groupings())} players advanced.", self.current_round_status()[2])
    
    def bracketed_generation(self):
        '''
        generate next round matches through bracket
        '''
        return gen_utils.group2(self.remaining_players)

    def seeded_generation(self):
        '''
        generate matches by seeds

        number of remaining participants must be base 2

        ex.
        8 -> 1v8, 2v7, 3v6, 4v5
        '''
        middle = int(len(self.remaining_players)/2)
        sorted_remaining = sorted(self.remaining_players, key=lambda player: player.getRating(), reverse=True)
        matches = list()
        
        for f, b in zip(range(middle), range(len(sorted_remaining)-1, middle-1, -1)):
            f = sorted_remaining[f]
            b = sorted_remaining[b]
            rand_num = rd.randint(0,1)
            match = [f, b] if rand_num == 0 else [b, f]
            matches.append(match)
        
        return matches
        
    def random_generation(self):
        remaining = copy.copy(self.remaining_players)
        rd.shuffle(remaining)
        next_round_matches = gen_utils.group2(remaining)
        return next_round_matches
    
    def process_winner(self, o_player):
        winner = None
        error = None

        if o_player.isnumeric() and (int(o_player)>len(self.players) or int(o_player) < 0):
            error = (o_player, None, "is not a valid player number")
            return winner, error
            
        player = gen_utils.try_get_player(o_player, self.players)
        if not player:
            error = (o_player, None, "is not a valid player")
            return winner, error
        if player not in self.remaining_players:
            error = (o_player, player, "is not in current round")
            return winner, error
        if player == self.winner:
            error = (o_player, player, "is already the winner")
            return winner, error

        self.current_advancements = [player]
        winner = player
        return winner, error
    
    def process_unadvancements(self, unadvanced):
        ua_players = 0
        errors = []

        for o_player in unadvanced:
            if o_player.isnumeric() and (int(o_player)>len(self.players) or int(o_player) < 0):
                errors.append((o_player, None, "player number doesn't exist"))
                continue

            player = gen_utils.try_get_player(o_player, self.players)
            if not player:
                errors.append((o_player, None, "player doesn't exist"))
                continue
            if player not in self.remaining_players:
                errors.append((o_player, player, "player is not in current round"))
                continue
            if player not in self.current_advancements or (self.winner and player!=self.winner):
                errors.append((o_player, player, "player has not been advanced"))
                continue

            ua_players+=1
            self.current_advancements.remove(player)
            if self.winner == player:
                self.winner = None

        return ua_players, errors

    def process_advancements(self, advanced):
        a_players = []
        errors = []
        for o_player in advanced:
            if o_player.isnumeric() and (int(o_player)>len(self.players) or int(o_player) < 0):
                errors.append((o_player, None, "player number doesn't exist"))
                continue

            player = gen_utils.try_get_player(o_player, self.players)
            if not player:
                errors.append((o_player, None, "player doesn't exist"))
                continue
            if player not in self.remaining_players:
                errors.append((o_player, player, "player is not in current round"))
                continue
            if player in self.current_advancements:
                errors.append((o_player, player, "player has already been advanced"))
                continue
            
            matchup = copy.copy([match for match in self.get_current_groupings() if player in match][0])
            matchup.remove(player)
            if matchup[0] in self.current_advancements:
                errors.append((o_player, player, "player's opponent has already been advanced"))
                continue

            a_players.append(player)
            self.current_advancements.append(player)

        return a_players, errors

    def matchups_to_str(self, matchups: List[List[Player.Player]]):
        '''
        Convert round matchups (list of lists) to a string.
        '''
        cur_round = "Preliminary Round" if self.round == 0 else f"Round {self.round} ({gen_utils.get_round_name(len(self.remaining_players))})"
        ret = cur_round + ("" if len(self.remaining_players)==2 else " Matchups") + "\n\n"

        if isinstance(matchups, tuple): #prelim round
            matchups, byes = matchups[0], matchups[1]

            ret+="Byes:\n"
            for b in byes:
                ret+=' - '+str(b)+'\n'
            ret+="\n"

        for i, match in enumerate(matchups):
            ret+=f"Match {i+1}: {discord_utils.disc_clean(match[0].get_full_display())}(A) vs. {discord_utils.disc_clean(match[1].get_full_display())}(DA)\n"
        
        return ret

    def get_round_results(self, round=-1, local_call=False):
        if len(self.round_advancements) == 0:
            return "Invalid round. No rounds have been finished."
        if round == -1: round = list(self.round_advancements.keys())[-1] #get last round's results

        try:
            assert(round in self.round_advancements)
        except AssertionError:
            return f"{round} is an invalid round: it must be from {list(self.round_advancements.keys())[0]}-{list(self.round_advancements.keys())[-1]}, or \"prelim\" if there was a preliminary round.", None

        round_data = self.__round_results(round, local_call=local_call)
        return ("Prelim Round" if round == 0 else f"Round {round}"), round_data
        
    def __round_results(self, round, local_call):
        if local_call: #local call by update_round_results (from Registration)
            matchups = []
            for num, match in enumerate(self.round_groupings[round]):
                player1 = match[0].get_full_display()
                player2 = match[1].get_full_display()
                match = [num+1, player1, player2] if match[0] in self.round_advancements[round] else [num+1, player2, player1]

                matchups.append(match)
            
            return matchups
        else:
            round_str = "Prelim Round" if round == 0 else f"Round {round} ({gen_utils.get_round_name(len(self.round_groupings[round])*2)})"
            ret = f"{round_str} Results\n{{}} = advanced player\n\n"
            for num, match in enumerate(self.round_groupings[round]):
                ret+=f"Match {num+1}: "
                if match[0] in self.round_advancements[round]:
                    ret+=f"{{{match[0].get_full_display()}}} vs. {match[1].get_full_display()}"
                else:
                    ret+=f"{match[0].get_full_display()} vs. {{{match[1].get_full_display()}}}"
                ret+="\n"

            return ret
                
    def get_tournament_results(self):
        '''
        get results of entire tournament, including each round's results and overall stats of the tournament
        ie. best player, average rating, etc. (can determine which stats to show)
        '''
        pass
    
    def current_round_status(self):
        '''
        get the status of the current round in progress.

        shows which players from matchups have already been advanced, and which matchups are still in progress.
        '''
        message = f"{len(self.current_advancements)}/{len(self.get_current_groupings())} matches finished in {'preliminary round' if self.round==0 else f'round {self.round} ({gen_utils.get_round_name(len(self.get_current_groupings())*2)})'}."

        finished_matches = []
        unfinished_matches = []

        for match in self.get_current_groupings():
            if match[0] in self.current_advancements or match[1] in self.current_advancements:
                finished_matches.append(match)
            else:
                unfinished_matches.append(match)
        
        ret = f"{len(unfinished_matches)} matches in progress:\n\n" if len(unfinished_matches)>0 else "0 matches in progress\n"

        for match in unfinished_matches:
            ret+=f"{match[0].get_full_display()} vs. {match[1].get_full_display()}\n"
        
        ret+= f"\n{len(finished_matches)} matches finished:\n{{}} = advanced player\n\n" if len(finished_matches)>0 else "\n0 matches finished"

        for match in finished_matches:
            if match[0] in self.current_advancements:
                    ret+=f"{{{match[0].get_full_display()}}} vs. {match[1].get_full_display()}"
            else:
                ret+=f"{match[0].get_full_display()} vs. {{{match[1].get_full_display()}}}"
            ret+="\n"
        
        return message, "Prelim Round" if self.round==0 else f"Round {self.round}", ret