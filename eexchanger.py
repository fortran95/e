# -*- coding: UTF-8 -*-
import os,sys,re,struct,time,subprocess,shelve
from ewindows import *
from esymmetric import *
from epgptranslator import *

BASEPATH = os.path.dirname(sys.argv[0])
if BASEPATH != '':
    BASEPATH += '/'

def send_new_key(keyselect_send,keyselect_recv):
    global BASEPATH
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
    key_hmackey = hashlib.sha512(engine.key).digest()
    key_fingerprint = hashlib.sha1(key_hmackey).hexdigest()
    key_timestamp = time.time()
    letter = struct.pack('72sf',engine.key,key_timestamp)
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
    # before returning, we have to store this key for ourselve.
    kd = shelve.open(BASEPATH + "symkeys.db",writeback=True)
    if kd.has_key(key_fingerprint):
        print "Oops! Aren\'t we randomized thoroughly? The key with same fingerprint already exists!"
        return False
    else:
        kd[key_fingerprint] = {'timestamp':key_timestamp,'key':engine.key,'sender':'','receiver':tkeyid,'trust':3,'hmackey':key_hmackey}
    kd.close()
    # return now.
    return 'SK' + inf
def load_new_key(keyinf):
    global BASEPATH
    if keyinf[0:2] != 'SK':
        print "Seems not a transfer key. Cancelled."
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
        keyinfo = struct.unpack('72sf',content)
        keyhmackey = hashlib.sha512(keyinfo[0]).digest()
        keyfingerprint = hashlib.sha1(keyinfo[0]).hexdigest()
        # Ask for user's opinion.
        accept = (loadKey(pgptrans) == 1)
        if not accept:
            print "User rejected this key."
            return False
    except:
        print "Unexcepted letter of transfer key."
        return False
    # Accept and save this.
    kd = shelve.open(BASEPATH + "symkeys.db",writeback=True)
    if kd.has_key(keyfingerprint):
        print "But the key with same fingerprint already exists!"
        return False
    else:
        #print "Trying to get sender info: %s" % pgptrans['sender']
        gpginfo = gpg_get_keys('--list-keys %s' % pgptrans['sender'], prefix='pub')
        
        kd[keyfingerprint] = {'timestamp':keyinfo[1],'key':keyinfo[0],'sender':gpginfo[0][0],'trust':pgptrans['trust'],'hmackey':keyhmackey}
    kd.close()
    print 'New key accepted and stored.'
    return True
if __name__ == '__main__':
    def ks_send(keys):
        return keySelect(keys,title='',description='即将签署一个新生成的通讯中继密钥。\n请选择您想要使用的PGP身份认证密钥。\n')
    def ks_recv(keys):
        return keySelect(keys,title='',description='请选择接收者的身份公钥。')
    load_new_key(send_new_key(ks_send,ks_recv))