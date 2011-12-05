#!python

import os
import platform
from slate.misc_lib import clean_files, create_folders

def main_program(select=None):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    create_folders(['./slate', './slate/rules', './storage', './extensions', './dAmnViper', './reflex', './stutter'])
    
    # PID stuff
    file = open('./storage/slate.pid', 'w')
    file.write(str(os.getpid()))
    file.close()
    
    if select is None:
        select = '--bot' if len(os.sys.argv) < 2 else os.sys.argv[1]
    
    import slate.menu
    slate.menu.run(select)
    
    clean_files()
    
if __name__ == '__main__':
    main_program()

# EOF
