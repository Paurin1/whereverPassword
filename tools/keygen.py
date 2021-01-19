from base64 import b64encode
from secrets import token_bytes

def get_bytes():
    return token_bytes(32)

def get_b64():
    return b64encode(token_bytes(16)).decode('ascii')

if __name__ == '__main__':
    tb = token_bytes(16)
    print(b64encode(tb).decode('ascii'))
    print(tb.hex())
    print(tb.hex().upper())