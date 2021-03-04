import rsa
import json
import pyaes

from base64 import b64encode, b64decode
from threading import Timer
from os.path import exists

KEY_SIZE = 2048
KEY_REFRESH_TIME = 5 * 60 # seconds

class RSA_Encryption:
    _key_public_client = None   # to encrypt messages
    _key_public_server = None   # to send to client
    _key_private_server = None  # to decrypt messages
    _key_refresh_timer = None

    def __init__(self):
        # load keys if they exist
        if exists('pub_key.pem') and exists('priv_key.pem'):
            self._key_public_client = rsa.PublicKey.load_pkcs1(open('pub_key.pem', 'rb').read())
            self._key_public_server = rsa.PublicKey.load_pkcs1(open('pub_key.pem', 'rb').read())
            self._key_private_server = rsa.PrivateKey.load_pkcs1(open('priv_key.pem', 'rb').read())

            # if saved key size does not match desired recreate the key
            if self._key_public_server.n.bit_length() != KEY_SIZE or self._key_private_server.n.bit_length() != KEY_SIZE:
                self.createNewKeys()

        # generate new keys
        else:
            self.createNewKeys()

        # set time point for key refreshment
        self._key_refresh_timer = Timer(KEY_REFRESH_TIME, self.refreshKey)

    def setClientsKey(self, key : str):
        ''' Sets _key_public_client value to a proper PublicKey object based
            on client's public key sent in base64 string format.
        '''
        self._key_public_client = rsa.PublicKey.load_pkcs1(bytes(
            '-----BEGIN RSA PUBLIC KEY-----\n' + key + '\n-----END RSA PUBLIC KEY-----\n'
        ))

    def createNewKeys(self):
        self._key_public_server, self._key_private_server = rsa.newkeys(KEY_SIZE)
        
        # save generated keys
        open('pub_key.pem', 'wb').write(self._key_public_server.save_pkcs1())
        open('priv_key.pem', 'wb').write(self._key_private_server.save_pkcs1())

    def refreshKey(self):
        self.createNewKeys()        
        self._key_refresh_timer = Timer(KEY_REFRESH_TIME, self.refreshKey)

    def encrypt(self, message : bytes) -> str:
        if not self._key_public_client:
            raise Exception("Missing client's public key")

        # calculate maximum message length
        max_length = int(self._key_public_client.n.bit_length() / 8) - 11 # key bytes minus 11 (random padding)

        # if message fits we can just encrypt it and send
        if len(message) <= max_length:
            return json.dumps({
                'msg': b64encode(rsa.encrypt(message, self._key_public_client)).decode('ascii'),
                'key': ''
            })

        # if message does not fit we need to:
        # 1. create random AES key
        # 2. encrypt message with AES key
        # 3. encrypt AES key with RSA
        # 4. pass encrypted AES key with message
        else:
            aes_key = rsa.randnum.read_random_bits(128)
            return json.dumps({
                'msg': b64encode(pyaes.Rijndael(aes_key).encrypt(message)).decode('ascii'),
                'key': b64encode(rsa.encrypt(aes_key, self._key_public_client)).decode('ascii')
            })

    def decrypt(self, message : str) -> bytes:
        if not self._key_private_server:
            raise Exception("Missing server's private key")

        # load message json content
        message = json.loads(message)

        # check if AES encryption is needed
        if len(message['key']) > 0:
            # decrypt key
            key = rsa.decrypt(b64decode(message['key']), self._key_private_server)

            # decrypt message
            return pyaes.Rijndael(key).decrypt(b64decode(message['msg']))

        else:
            return rsa.decrypt(b64decode(message['msg']), self._key_private_server)

    def decryptKey(self, key_message : str) -> bytes:
        if not self._key_private_server:
            raise Exception("Missing server's private key")

        # extract bytes from hex string key
        key_bytes = bytes.fromhex(key_message)

        # create int variable from given bytes
        num = int.from_bytes(key_bytes, byteorder='big')

        # perform decryption
        # m = e^d mod n
        dec = pow(num, self._key_private_server.d, self._key_private_server.n)

        return dec.to_bytes(length=16, byteorder='big')
