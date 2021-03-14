import rsa
import json
import pyaes

from base64 import b64encode, b64decode
from os.path import exists

KEY_SIZE = 2048

class RSA_Encryption:
    key_public = None
    key_private = None

    # to rsa.js file rendering
    key_n = None
    key_e = None

    def __init__(self):
        # load keys if they exist
        if exists('wp_pub_key.pem') and exists('wp_priv_key.pem'):
            self.key_public = rsa.PublicKey.load_pkcs1(open('wp_pub_key.pem', 'rb').read())
            self.key_private = rsa.PrivateKey.load_pkcs1(open('wp_priv_key.pem', 'rb').read())

            self.key_n = hex(self.key_public.n)[2:]
            self.key_e = hex(self.key_public.e)[2:]

            # if saved keys sizes does not match the desired ones -> recreate keys
            if self.key_public.n.bit_length() != KEY_SIZE or self.key_private.n.bit_length() != KEY_SIZE:
                self.createNewKeys()

        # generate new keys
        else:
            self.createNewKeys()

    def createNewKeys(self):
        self.key_public, self.key_private = rsa.newkeys(KEY_SIZE)
        self.key_n = hex(self.key_public.n)[2:]
        self.key_e = hex(self.key_public.e)[2:]
        
        # save generated keys
        open('wp_pub_key.pem', 'wb').write(self.key_public.save_pkcs1())
        open('wp_priv_key.pem', 'wb').write(self.key_private.save_pkcs1())

    # encrypts message of any size
    def encrypt(self, message : bytes) -> str:
        if not self.key_public:
            raise Exception("Missing public key")

        # calculate the maximum message length
        max_length = int(self.key_public.n.bit_length() / 8) - 11 # key bytes minus 11 (random padding)

        # if the message fits we can just encrypt it and send
        if len(message) <= max_length:
            return json.dumps({
                'msg': b64encode(rsa.encrypt(message, self.key_public)).decode('ascii'),
                'key': ''
            })

        # if message does not fit we need to:
        # 1. create random AES key
        # 2. encrypt message with AES key
        # 3. encrypt AES key with RSA
        # 4. pass encrypted AES key with the message
        else:
            aes_key = rsa.randnum.read_random_bits(128)
            return json.dumps({
                'msg': b64encode(pyaes.Rijndael(aes_key).encrypt(message)).decode('ascii'),
                'key': b64encode(rsa.encrypt(aes_key, self.key_public)).decode('ascii')
            })

    def decrypt(self, message : str) -> bytes:
        if not self.key_private:
            raise Exception("Missing private key")

        # load message's json string
        message = json.loads(message)

        # check if AES encryption is needed
        if len(message['key']) > 0:
            # decrypt key
            key = rsa.decrypt(b64decode(message['key']), self.key_private)

            # decrypt message
            return pyaes.Rijndael(key).decrypt(b64decode(message['msg']))

        else:
            return rsa.decrypt(b64decode(message['msg']), self.key_private)

    # this function skips built-in RSA decrypt function
    # it does not take into account message validation
    # it just performs lowest-possible level decryption
    def decryptKey(self, key_message : str) -> bytes:
        if not self.key_private:
            raise Exception("Missing private key")

        # extract bytes from the hex string key
        key_bytes = bytes.fromhex(key_message)

        # create int variable from extracted bytes
        num = int.from_bytes(key_bytes, byteorder='big')

        # perform decryption
        # m = e^d mod n
        dec = pow(num, self.key_private.d, self.key_private.n)

        return dec.to_bytes(length=16, byteorder='big')

# if you run this file it will create RSA Public and Private keys
if __name__ == '__main__':
    RSA_Encryption()