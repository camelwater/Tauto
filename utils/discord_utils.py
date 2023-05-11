import io
import os
from collections import namedtuple
import discord

SETTING_VALUES = {
    'defaultSeeding': {
        0: 0, 
        "f": 0,
        "false": 0,
        "no": 0, 
        "n": 0,
        1: 1, 
        "t": 1,
        "true": 1, 
        "yes": 1, 
        "y": 1
    }, 
    'defaultBracket':{
        0: 0, 
        "f": 0,
        "false": 0,
        "no": 0, 
        "n": 0,
        1: 1, 
        "t": 1,
        "true": 1, 
        "yes": 1, 
        "y": 1
    }
}

SPLIT_DELIM = '{d/D17¤85xu§ey¶}'
DEFAULT_PREFIXES = [';', ',']

TOURNAMENT_TYPES = namedtuple('Tournament', ['SINGLE', 'DOUBLE', 'CL'])


def create_temp_file(filename, content, dir='.', no_ret = False):
    with open(dir+filename, 'w', encoding='utf-8') as e_file:
        e_file.write(content)
    if no_ret: return
    return io.BytesIO(open(dir+filename, 'rb').read())

def delete_file(filename):
    try:
        os.remove(filename)
    except (FileNotFoundError,IsADirectoryError):
        pass

async def send_file(ctx, file_content, dir, filename):
    filename = filename.replace(' ', '_').lower() 
    r_file = create_temp_file(filename, file_content, dir=dir)
    delete_file(dir+filename)
    await ctx.send(file = discord.File(fp=r_file, filename=filename))

def disc_clean(msg: str):
    return msg.replace("*", "\*").replace("`",'\`').replace("_", "\_").replace("~~", "\~~")

def convert_str_to_tournament(option_str: str):
    
    single_terms = {'singleelimination', 'single', 'se', 'singleelim'}
    double_terms = {'doubleelimination', 'double', 'de', 'doubleelim'}
    cl_terms = {'championsleague', 'cl', 'champions'}

    option = option_str.lower().replace(" ", "")
    if option in single_terms:
        return TOURNAMENT_TYPES.SINGLE
    elif option in double_terms:
        return TOURNAMENT_TYPES.DOUBLE
    elif option in cl_terms:
        return TOURNAMENT_TYPES.CL
    raise KeyError

