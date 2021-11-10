from Player import Player
from generator import Generator
import Utils

ratings = [1000, 750, 650, 800, 1400, 1700, 950, 900, 925, 1200]
ratings2 = [None, None, 1000, 1400, 1200, 800, 750, None, 1600, 1500, 800, 700, 500, 450]
players = list()
# print(Utils.calculate_std_dev(ratings))

for id, rating in enumerate(ratings2):
    players.append(Player(id+1, f"PLAYER {id+1}", rating=rating))

tournament = Generator(players=players, is_open=True, random=False)

tournament.start()

print(tournament.current_round_status())

while True:
    if len(tournament.remaining_players) <=2:
        break
    advanced = input("advance: ").split(",")
    advanced = [p.strip() for p in advanced]

    tournament.next_round(advanced = advanced)

    print(tournament.current_round_status())

