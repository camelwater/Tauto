from Player import Player
from generator import Generator
import utils.gen_utils as gen_utils

ratings = [1000, 750, 650, 800, 1400, 1700, 950, 900, 925, 1200]
ratings2 = [None, None, 1000, 1400, 1200, 800, 750, None, 1600, 1500, 800, 700, 500, 450, None, None, 650, 550, 575, 990, 1125, 1325, 1500]
players = list()
# print(Utils.calculate_std_dev(ratings))

for id, rating in enumerate(ratings2):
    players.append(Player(id+1, f"PLAYER {id+1}", rating=rating))

tournament = Generator(players=players, is_open=True, random=False)

print("PLAYERS:",len(tournament.players))
print(f"NUM ROUNDS: {tournament.total_rounds}" + (" + prelim round" if tournament.has_prelim else ""))
print()

tournament.start()

print(tournament.current_round_status())

while True:
    if len(tournament.remaining_players) <=2:
        break
    
    while True:
        advanced_raw = input("advance: ")
        if "next" in advanced_raw:
            if tournament.round_finished():
                break
            print("\nnot all matches have finished\n")
            continue
        
        advanced = advanced_raw.split(",")
        advanced = [p.strip() for p in advanced]
        tournament.advance(advanced)

    tournament.next_round()

    print(tournament.current_round_status())

