import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


class crypt_engine:
    fake_mess = b"@#ERROR~Its FaKe T!me"
    def __init__(self, password, cs, salt=b""):
        self.password=password
        self.cs = cs
        if salt == b"":
            salt = os.urandom(16)
        kdf = Argon2id(salt=salt, length=32, iterations=2, lanes=4, memory_cost=65536)
        self.key = kdf.derive(password.encode("utf-8"))
        self.salt = salt

    def encrypt(self, txt):

        if(not self.password):
            return txt

        key = self.key
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        cipher = nonce + aesgcm.encrypt(nonce, txt, associated_data=None)
        return cipher

    def decrypt(self, cipher):

        if(not self.password):
            return cipher

        if cipher == b'':
            return b''

        key = self.key
        aesgcm = AESGCM(key)
        nonce = cipher[:12]
        actual_ciphertext = cipher[12:]
        try:
            return aesgcm.decrypt(nonce, actual_ciphertext, associated_data=None)
        except:
            return self.fake_mess

    def size(self, s):
        if(not self.password):
            return s
        cs=self.cs
        return s+28*(s//cs+(s%cs!=0))