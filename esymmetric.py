import random,hashlib,hmac

class symmetric(object):
    secret = ''
    def __init__(self):
        pass
    def generate(self,bits=1024):
        self.secret = random.getrandbits(bits)
    def encrypt(self,plaintext):
        # Force using HMAC to check
        hmackey = hashlib.sha512(self.secret).digest()
        pass
    def decrypt(self,ciphertext):
        pass
    