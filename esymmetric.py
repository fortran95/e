import random,hashlib,hmac,M2Crypto,shelve,os,ConfigParser,time,base64
from Crypto.Cipher import *
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
class symmetric(object):
    version = 0.0
    key = ''
    def __init__(self,key=''):
        if len(key)<72:
            self.key = M2Crypto.Rand.rand_bytes(72)
        else:
            self.key = key
    def encrypt(self,plaintext):
        if len(self.key)<72:
            return False
        # Initilize iv, HMAC_key
        hmackey = hashlib.sha512(self.key).digest()
        iv = M2Crypto.Rand.rand_bytes(40)
        
        cipher1 = Blowfish.new(self.key[0:16], Blowfish.MODE_CBC,iv[0:8])
        cipher2 = AES.new(self.key[16:32], AES.MODE_CBC, iv[8:24])
        cipher3 = CAST.new(self.key[32:48], CAST.MODE_CBC, iv[24:32])
        cipher4 = DES3.new(self.key[48:72], DES3.MODE_CBC, iv[32:40])
        
        ciphertext1 = cipher1.encrypt(self._enpad(plaintext))
        ciphertext2 = cipher2.encrypt(ciphertext1)
        ciphertext3 = cipher3.encrypt(ciphertext2)
        ciphertext4 = cipher4.encrypt(ciphertext3)
        hmacvalue = hmac.HMAC(hmackey,ciphertext4,hashlib.sha512).digest()
        
        return iv + hmacvalue + ciphertext4
    def decrypt(self,ciphertext):
        if len(ciphertext) < 120:
            return False
        hmackey = hashlib.sha512(self.key).digest()
        iv = ciphertext[0:40]
        hmacvalue = ciphertext[40:104]
        src = ciphertext[104:]
        
        if len(src) % 16 != 0:
            return False
        
        calc_hmac = hmac.HMAC(hmackey,src,hashlib.sha512).digest()
        
        if calc_hmac != hmacvalue:
            return False
        
        cipher1 = Blowfish.new(self.key[0:16], Blowfish.MODE_CBC,iv[0:8])
        cipher2 = AES.new(self.key[16:32], AES.MODE_CBC, iv[8:24])
        cipher3 = CAST.new(self.key[32:48], CAST.MODE_CBC, iv[24:32])
        cipher4 = DES3.new(self.key[48:72], DES3.MODE_CBC, iv[32:40])
        
        ciphertext3 = cipher4.decrypt(src)
        ciphertext2 = cipher3.decrypt(ciphertext3)
        ciphertext1 = cipher2.decrypt(ciphertext2)
        plaintext = cipher1.decrypt(ciphertext1)
       
        return self._depad(plaintext)
        
    def _enpad(self,input):
        readcheck = hashlib.md5(input).digest()
        padlen = 16 - (len(input) + 17) % 16
        if padlen == 16:
            padlen = 0
        return readcheck + chr(padlen) + input + chr(padlen) * padlen
    
    def _depad(self,input):
        l = len(input)
        if l < 17:
            return False
        
        readcheck = input[0:16]
        padlen = ord(input[16:17])
        input = input[17:l-padlen]
        calchash = hashlib.md5(input).digest()
        if readcheck != calchash:
            return False
        else:
            return input
def list_all_keys():
    # Aims at listing all possible transfer-keys.
    # These info should be provided.
    #  - Key ID
    #  - Timestamp
    #  - Advice: 1) Should discard 2) Should avoid using
    #  - Where did we received it, and how was that trusted.
    #    or, to whom we have sent this key.
    #gpg_private_keys = gpg_get_keys()
    #gpg_public_keys = gpg_get_keys(command='--list-public-keys',prefix='pub')
    symkeys = shelve.open('symkeys.db',writeback=True)
    config = ConfigParser.ConfigParser()
    config.read('e.conf')

    tkey_life = config.getint('TransferKey Rules','life')
    tkey_old = config.getfloat('TransferKey Rules','old')
    if tkey_old <= 0 or tkey_old > 1:
        print "Invalid configured: TransferKey Rules->old, should be (0,1)."
        return False
    if tkey_life <= 180:
        print "Invalid configured: TransferKey Rules->life, should > 180."
        return False
    tkey_old = tkey_old * tkey_life
    now = time.time()

    ret = {}
    for key_fingerprint in symkeys:
        keyinfo = symkeys[key_fingerprint]
        group_id = ''
        
        # The following is of EXTREMELY importance in understanding the protocol
        if keyinfo['sender'] == '':# This is a key we sent to others.
            group_id = keyinfo['receiver']
        else:   # This is a key we received from other.
            group_id = keyinfo['sender']
        
        this_keyinfo = {'key':keyinfo['key'],'trust':keyinfo['trust'],'timestamp':keyinfo['timestamp'],'old':True}
        
        if ret.has_key(group_id):
            ret[group_id]['keys'][key_fingerprint] = this_keyinfo
        else:
            ret[group_id] = {'keys':{key_fingerprint:this_keyinfo}}
    for group_id in ret:
        has_new_key = False
        has_key = False
        for key_fingerprint in ret[group_id]['keys']:
            # TODO check usability.
            if now - ret[group_id]['keys'][key_fingerprint]['timestamp'] < tkey_life:
                has_key = True
                if now - ret[group_id]['keys'][key_fingerprint]['timestamp'] < tkey_old:
                    has_new_key = True
                    ret[group_id]['keys'][key_fingerprint]['old'] = False
            else:
                # Expired keys will lost its info.
                ret[group_id]['keys'][key_fingerprint]['key'] = ''
                symkeys[key_fingerprint]['key'] = ''
        ret[group_id]['has_new_key'] = has_new_key
        ret[group_id]['has_key'] = has_key
    return ret
def send_message(keyID,message):
    # Use sym key to send a message. Receiver is one of the public key ID.
    allkeys = list_all_keys()
    if allkeys.has_key(keyID) == False:
        print "Invalid parameter when sending message: [%s] is unknown. You may try exchange a key with it." % keyID
        return False
    selected_group = allkeys[keyID]
    if selected_group['has_new_key'] == False:
        print "You need to exchange a key to [%s] first." % keyID
        return False
    for keyid in selected_group['keys']:
        if selected_group['keys'][keyid]['old'] == False:
            break
    selectedkey = selected_group['keys'][keyid]
    print "Found a proper key [FINGERPRINT:%s]. Will use this to encrypt." % keyid
    encryptor = symmetric(selectedkey['key'])
    message = keyid + '\n' + base64.encodestring(encryptor.encrypt(message))
    return message
def read_message(message):
    try:
        keyid = message[0:40].strip()
        message = base64.decodestring(message[40:].strip())
        allkeys = list_all_keys()
        decrypted = False
        for gid in allkeys:
            if allkeys[gid]['keys'].has_key(keyid):
                foundkey = allkeys[gid]['keys'][keyid]
                if foundkey['key'] != '':
                    decryptor = symmetric(foundkey['key'])
                    decrypted = decryptor.decrypt(message)
                else:
                    print "Cannot decrypt the message, key expired."
                break
        if decrypted != False:
            return {'keyID':gid,'message':decrypted}
    except:
        pass
if __name__ == '__main__':
    print read_message(send_message('7BC95BF8','test string'))