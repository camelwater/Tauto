from math import sqrt
from statistics import mean
import random as rd

def is_advanced(player, advanced_group):
    advanced_group_lowered = [p.lower() for p in advanced_group]
    return player.getName().lower() in advanced_group_lowered or str(player.getID()) in advanced_group or str(player.getDiscordID) in advanced_group
    
def group2(players, shuffle_color=True):#UTILS
    groups = list(chunks(players, 2))
    if shuffle_color:
        for group in groups:
            rd.shuffle(group)
        return groups
    return groups

def chunks(l, n):
    """
    split list into consecutive n-sized chunks
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]

def calculate_std_dev(collection):
    return sqrt(__calculate_variance(collection, mean(collection)))

def __calculate_variance(collection, mean):
    return sum(list(map(lambda k: (k-mean)**2, collection)))/(len(collection)-1)


def next_power2(x):
    return 1<<(x-1).bit_length()