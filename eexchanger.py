# -*- coding: UTF-8 -*-
import os,re,struct,time,subprocess
from ewindows import *
from esymmetric import *
from epgptranslator import *

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
    f = open("tempinfo_newkey","w+")
    f.write(letter)
    f.close()
    os.popen("gpg2 --default-key 0x%s --recipient 0x%s -q -es tempinfo_newkey" % (mykeyid, tkeyid))
    os.remove("tempinfo_newkey")
    #print letter
    f = open("tempinfo_newkey.gpg","r")
    inf = f.read()
    f.close()
    os.remove("tempinfo_newkey.gpg")
    return 'SK' + inf
def load_new_key(keyinf):
    if keyinf[0:2] != 'SK':
        return False
    keyinf = keyinf[2:]
    # Write down to file
    f = open("tempinfo_readkey","w+")
    f.write(keyinf)#[0:30] + '000' * 10 + keyinf[-30:])#keyinf)
    f.close()
    # fire PGP to decrypt & verify
    pgpsaid = ''
    content = ''
    pipe = os.popen("gpg2 --status-file tempinfo_readkey_status --decrypt tempinfo_readkey")
    content = pipe.read()
    pipe.close()
    os.remove("tempinfo_readkey")
    # Read PGP status
    f = open("tempinfo_readkey_status","r")
    pgpsaid = f.read()
    f.close()
    os.remove("tempinfo_readkey_status")
    # Figure out what PGP said.
    pgptrans = pgp_translator(pgpsaid)
    if pgptrans['valuable'] == False:
        print "Received data worths nothing. Exit."
        return False
    try:
        keyinfo = struct.unpack('72sf8s',content)
        # Ask for user's opinion.
        accept = (loadKey(pgptrans) == 1)
        if not accept:
            print "User rejected this key."
            return False
    except ex:
        print "Unexcepted letter of transfer key."
        return False
    # Accept and save this.
    print "TODO: SAVE THE KEY."
if __name__ == '__main__':
    def ks_send(keys):
        return keySelect(keys,title='',description='即将签署一个新生成的通讯中继密钥。\n请选择您想要使用的PGP身份认证密钥。\n')
    def ks_recv(keys):
        return keySelect(keys,title='',description='请选择接收者的身份公钥。')
    load_new_key(send_new_key(ks_send,ks_recv))