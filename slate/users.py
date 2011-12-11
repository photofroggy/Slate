''' slate.users
    Created by photofroggy
    
    Manages user privileges for the bot.
'''

import os
import json
from slate.misc_lib import export_struct

class UserManager(object):
    
    def __init__(self, file='./storage/users.bsv', stdout=None, stddebug=None):
        self.file = file
        self.owner = None
        
        def ddebug(msg, *args):
            pass
        
        self.write = stdout or ddebug
        self.debug = stddebug or ddebug
        self.map = []
        self.groups = Groups()
    
    def log(self, msg, *args):
        self.debug(msg, showns=False, *args)
    
    def load(self, owner=None):
        if owner is not None:
            self.owner = owner
            
        self.log('** Loading user data...')
        if not os.path.exists(self.file):
            self.log('>> No user data found! Setting default user list!')
            self.map = self.defaults()
            self.load_groups()
            self.save()
        else:
            file = open(self.file, 'r')
            self.map = json.loads(file.read())
            file.close()
            self.load_groups()
        
        self.remove(self.owner)
        self.add(self.owner, 'owner')
        self.log('** User data loaded.')
    
    def save(self):
        self.log('** Saving user data...')
        self.save_groups()
        file = open(self.file, 'w')
        file.write(export_struct(self.map))
        file.close()
        self.log('** User data saved.')
    
    def load_groups(self):
        grps = [[grp[0], grp[1]] for grp in self.map]
        self.groups.set(grps)
    
    def save_groups(self):
        grps = self.groups.get()
        for i in range(0, len(grps)):
            self.map[i][0] = grps[i][0]
            self.map[i][1] = grps[i][1]
    
    def defaults(self):
        return [
            ['Banned', None, []],
            ['Guests', None, []],
            ['Members', None, []],
            ['Operators', None, []],
            ['Owner', None, [] if self.owner is None else [self.owner]],
        ]
    
    def find(self, user, name=False):
        for i, group in enumerate(self.map):
            for privd in group[2]:
                if privd.lower() == user.lower():
                    if name:
                        return group[1] or group[0]
                    return i
        return 1 if not name else self.groups.name(1)
    
    def has(self, user, group=None):
        user_priv = self.find(user)
        
        if group is None:
            return user_priv
        
        priv = self.groups.find(group)
        
        return user_priv >= priv
    
    def add(self, user, group):
        """Add user to group."""
        if not user or not group:
            return False
        
        user, group = user.lower(), group.lower()
        if user == self.owner.lower():
            return False
        
        if group == 'owner':
            return False
        
        group = self.groups.find(group, True)
        if group is None:
            return False
        
        gindex = self.groups.find(group)
        if self.map[gindex][0] == 'Guests':
            return True
        
        if not self.find(user) in [1, gindex]:
            self.remove(user)
        
        self.map[gindex][2].append(user)
        self.save()
        
        return True
    
    def remove(self, user):
        """Remove user from the user list."""
        if not user:
            return False
        
        user = user.lower()
        if user == self.owner.lower():
            return False
        
        group = self.find(user)
        if group == 1:
            return False
        
        self.map[group][2].pop(self.map[group][2].index(user))
        self.save()
        
        return True
    

class Groups:
    
    def __init__(self):
        self.groups = []
    
    def set(self, seq):
        self.groups = seq
    
    def get(self):
        return self.groups
    
    def set_alias(self, group, alias=None):
        index = self.find(group)
        if index < 0:
            return False
        self.groups[index][1] = alias
        return True
    
    def find(self, group, name=False):
        group = group.lower()
        
        for i, grp in enumerate(self.groups):
            for gname in grp[:2]:
                if gname is None:
                    continue
                
                if gname.lower() == group:
                    return i if not name else gname
                    
        return -1 if not name else None
    
    def name(self, num):
        if num < 0 or num >= len(self.groups):
            return None
        return self.groups[num][1] or self.groups[num][0]


# EOF
