import random,hashlib,hmac,M2Crypto,shelve,os
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
    gpg_private_keys = gpg_get_keys()
    gpg_public_keys = gpg_get_keys(command='--list-public-keys',prefix='pub')
    
    pass
if __name__ == '__main__':
    list_all_keys()
    