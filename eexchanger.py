import os,re
from ewindows import *
from esymmetric import *

class exchanger(object):
    def __init__(self):
        pass
    def send(self):
        pass
    
def send_new_key(keyselect):
    # This will use console as interface.
    #  first, ask for receiver's id.
    keylist = os.popen('gpg2 --list-secret-keys')
    readbegin = False
    
    keyid = ''
    keydate = ''
    keydes = ''
    
    keys = []
    while True: #fire GPG to list all secret keys
        l = keylist.readline()
        if l == '':
            break
        else:
            if l[0:3] == 'sec':
                readbegin = True
            if readbegin:
                if l == '\n':
                    readbegin = False
                    # dumpbuffer
                    keys.append([keyid,keydate,keydes])
                    keyid = ''
                    keydate = ''
                    keydes = ''
                # Fetch info for each key.
                if l[0:3] == 'sec':
                    keypar = l[3:].strip().split(' ')
                    keyid = keypar[0][-8:]
                    keydate = keypar[1]
                elif l[0:3] == 'uid':
                    keydes += l[3:].strip()
    # Ask for selection
    selectid = keyselect(keys)
    if selectid < 0:
        print 'User cancelled key-sending sequence.'
        return False
    key = keys[selectid]
    # Generate new key and save it.
    engine = symmetric()
    print engine.key

if __name__ == '__main__':
    send_new_key(keySelect)