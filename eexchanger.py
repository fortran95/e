import os,re,struct,time
from ewindows import *
from esymmetric import *

def gpg_get_keys(command='--list-secret-keys',prefix='sec'):
    keylist = os.popen('gpg2 %s' % command)
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
            if l[0:3] == prefix:
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
                if l[0:3] == prefix:
                    keypar = l[3:].strip().split(' ')
                    keyid = keypar[0][-8:]
                    keydate = keypar[1]
                elif l[0:3] == 'uid':
                    keydes += l[3:].strip()
    return keys
def send_new_key(keyselect_send,keyselect_recv):
    # This will use console as interface.
    #  first, ask for receiver's id.
    mykeys = gpg_get_keys()
    tkeys = gpg_get_keys(command='--list-public-keys',prefix='pub')
    # Ask for selection
    myselectid = keyselect_send(mykeys)
    if myselectid < 0:
        print 'User cancelled key-sending sequence.'
        return False
    tselectid = keyselect_recv(tkeys)
    if tselectid < 0:
        print 'User cancelled key-sending sequence.'
        return False
    mykey = mykeys[myselectid]
    tkey = tkeys[tselectid]
    # Generate new key
    engine = symmetric()
    # Write a letter
    mykeyid = mykey[0]
    tkeyid = tkey[0]
    letter = struct.pack('72sf8s',engine.key,time.time(),mykeyid)
    # Fire PGP to sign and encrypt the letter.
    f = open("tempinfo","w+")
    f.write(letter)
    f.close()
    os.popen("gpg2 --armor --default-key 0x%s --recipient 0x%s -q -es tempinfo" % (mykeyid, tkeyid))
    os.remove("tempinfo")
    #print letter
    f = open("tempinfo.asc","r")
    inf = f.read()
    f.close()
    os.remove("tempinfo.asc")
    return inf

if __name__ == '__main__':
    def ks_send(keys):
        return keySelect(keys,title='',description='You are going to sign a new transfer-key.\nPlease select the identifing PGP secret key that you want to use.\n')
    def ks_recv(keys):
        return keySelect(keys,title='',description='Choose your recipient\'s key.')
    print send_new_key(ks_send,ks_recv)