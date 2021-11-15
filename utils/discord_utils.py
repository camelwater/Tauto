import io
import os


SETTING_VALUES = {
    'defaultOpen': {
        1: 1,
        "1": 1, 
        "t": 1, 
        "yes": 1, 
        "y": 1,
        0: 0, 
        "0": 0, 
        "f": 0,
        "no": 0, 
        "n": 0
    }
}

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

def disc_clean(msg: str):
    return msg.replace("*", "\*").replace("`",'\`').replace("_", "\_").replace("~~", "\~~")