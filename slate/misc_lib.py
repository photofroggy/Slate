''' slate.misc_lib
    Created by photofroggy (Henry Rapley)
    Released under GNU GPL v3.
    
    This module contains various methods
    that do not belong anywhere else inside
    the structure of the program.
'''

import os
import time
import datetime
from math import floor

''' >>>>>>>>>>>>> DATA MANIPULATIONS <<<<<<<<<<<<<<<<<<
    The following methods manipulate data in a useful way.
'''

def export_struct(data, depth=1):
    """ This method returns a JSON object from a Python object.
        The JSON object is formatted to make it easier to read.
        Example: export_struct({'lol':[1,2]})
            >>  {
            >>      'lol': [
            >>          1,
            >>          2
            >>      ]
            >>  }
    """
    if isinstance(data, dict):
        string  = '{'
    elif isinstance(data, list) or isinstance(data, tuple):
        string = '['
    else:
        return flatten_val(data)
    for i in data:
        if len(string) > 0 and string[-1] not in ('{', '(', '['):
            string+= ','
        string += '\n{0}'.format("    " * depth)
        if isinstance(data, dict):
            string += flatten_val(i)+' : '
            use = data[i]
        else:
            use = i
        if isinstance(use, str) or isinstance(use, int) or isinstance(use, float):
            string += flatten_val(use)
        else:
            string += export_struct(use, depth+1)
    if len(data) > 0: string += "\n"+("    "*(depth-1))
    if isinstance(data, list) or isinstance(data, tuple):
        string += ']'
    elif isinstance(data, dict):
        string += '}'
    return string

def flatten_val(value):
    if not isinstance(value, str):
        if value is None:
            return 'null'
        if value is True:
            return 'true'
        if value is False:
            return 'false'
        return str(value)
    return '"{0}"'.format(str(value).replace('"', '\\"'))
    
def human_list(sequence):
    """ This returns a list of items as a grammatically correct string!
        Examples:
            human_list(['one', 'two']) => 'one and two'
            human_list(['one', 'two', 'three']) => 'one, two and three'
            human_list(['one', 'two', 'three', 'four']) => 'one, two, three and four'
    """
    if len(sequence) == 0:
        return ''
    sequence = [str(i) for i in sequence]
    if len(sequence) == 2:
        return ' and '.join(sequence)
    if len(sequence) > 2:
        return ' and '.join([', '.join(sequence[:-1]), sequence[-1]])
    return sequence[0]

''' >>>>>>>>>>>>> TIME STAMP MANIPULATIONS <<<<<<<<<<<<<<<<<<
    The following methods are related to time
    stamps and various representations.
'''

class timelen_tuple(tuple):
    """Just a type definition."""
    pass

def timelen(seconds):
    """timelen(int) returns tuple (years, weeks, days, hours, minutes, seconds)."""
    seconds = int(seconds)
    seconds = seconds * -1 if seconds < 0 else seconds
    formats = [ 31556926, 604800, 86400, 3600, 60, 1 ]
    lens = []
    for format in formats:
        if seconds >= format:
            num = floor(seconds / format)
            seconds = seconds % format
            lens.append(int(num if num > 0 else 0))
        else: lens.append(0)
    return timelen_tuple(lens)

def timelen_until(year, month, day):
    """timelen_tuple(month, day) returns a timelen tuple defining the time length until the next date "day of month"."""
    timetuple = time.strptime(str(year) + str(month) + str(day), '%Y%m%d')
    diff = timelen(int(time.mktime(timetuple))-int(time.time()))
    return timelen_tuple([diff[0], diff[1], diff[2], 0, 0, 0])

def strftimelen(tl):
    """strftimelen() returns a formatted string from a time length. Accepts integers or timelen_tuples."""
    if not isinstance(tl, tuple):
        try: tl = timelen(int(tl))
        except TypeError: pass
    strs = ['year', 'week', 'day', 'hour', 'minute', 'second']
    out = human_list(
        [' '.join((str(tl[i]), name + ('' if tl[i] == 1 else 's'))) for i, name in enumerate(strs) if tl[i] > 0]
    )
    return '0 seconds' if out == '' else out

def intftimelen(tl):
    """intftimelen(timelen) returns a length of time in seconds."""
    formats = [ 31556926, 604800, 86400, 3600, 60, 1 ]
    lens = 0
    for i, num in enumerate(tl):
        num = floor(num * formats[i])
        lens+= int(num if num > 0 else 0)
    return lens
    
''' >>>>>>>>>>>>>>>>> END TIMESTAMP MANIPULATIONS <<<<<<<<<<<<<<<<<<<<< '''
    
def arguments(data=False, start=0, finish=False, separator=' ', sequence=False):
    """ This method extracts specific arguments from a message. """
    if data == '':
        return '' if not sequence else ['']
    
    data = data.split(separator)
    
    if len(data) <= start:
        return '' if not sequence else ['']
    if isinstance(finish, bool) or finish == None:
        data = data[start:] if finish else [data[start]]
    else:
        data = data[start:] if len(data) <= finish else data[start:finish]
    return data if sequence else separator.join(data)
    
''' >>>>>>>>>>>>> DIRECTORY MANIPULATIONS <<<<<<<<<<<<<<<<<<
    These methods manipulate files and directories.
'''

def clean_files(dirs=['.', './terra', './terra', './storage', './extensions', './dAmnViper', './reflex', './rules']):
    """ Removes .pyc files from given directories. """
    for dir in dirs:
        for file in os.listdir(dir):
            name, ext = os.path.splitext(file)
            if ext == '.pyc':
                if os.path.exists(os.path.join(dir, name+'.py')):
                    os.remove(os.path.join(dir, file))

def create_folders(folders, mode=0o755):
    """ Creates the given folders. Avoiding errors along the way. """
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder, mode)
            continue
        os.chmod(folder, mode)

''' >>>>>>>>>>>>>>>> IO OPERATIONS <<<<<<<<<<<<<<<<<<<<<<<<<<
    Just one or two methods used for IO.
'''
    
def get_input(prefix='> ', empty=False):
    while True:
        ins = input(prefix).rstrip('\r')
        if (len(ins) == 0 and empty) or len(ins) > 0:
            return ins

# EOF
