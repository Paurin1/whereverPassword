from base64 import b64encode
from secrets import token_bytes

def get_bytes():
    return token_bytes(32)

def get_b64():
    return b64encode(token_bytes(32)).decode('ascii')

if __name__ == '__main__':
    print(b64encode(token_bytes(32)).decode('ascii'))