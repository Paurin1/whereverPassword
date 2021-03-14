from base64 import b64encode
from hashlib import md5
from random import randint

def token_bytes(size):
    ints = []
    for _ in range(size):
        ints.append(randint(0, 255))
    return bytes(ints)

def get_bytes(size=16):
    return token_bytes(size)

def get_b64(size=16):
    return b64encode(token_bytes(size)).decode('ascii')

def hashKey(key):
    rounds_count = 128 * key[0] + key[1]
    for _ in range(rounds_count):
        key = md5(key).digest()
    return key.hex()

if __name__ == '__main__':
    tb = token_bytes(16)
    print(b64encode(tb).decode('ascii'))
    print(tb.hex())
    print(tb.hex().upper())