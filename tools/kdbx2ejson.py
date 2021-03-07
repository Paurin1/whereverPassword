import base64
import json
import pyaes
import sys
import keygen
from hashlib import md5
from os import path

from pykeepass import PyKeePass

# python kdbx2ejson.py [kbdx file] [key file / password] [hex key]
args = sys.argv

# check if its a keyfile or password
kf = None; pwd = None
if path.exists(args[2]):
    kf = args[2]
else:
    pwd = args[2]

kp = PyKeePass(args[1], keyfile=kf, password=pwd)

entries = []

for entry in kp.entries:
    entries.append({
        'name': entry.title,
        'url': entry.url,
        'username': entry.username,
        'password': base64.b64encode(entry.password.encode('utf-8')).decode('ascii')
    })

if len(args) == 4:
    aes = pyaes.Rijndael(bytes.fromhex(args[3]))
else:
    key = keygen.get_b64()
    aes = pyaes.Rijndael(base64.b64decode(key))
    print(key)

ret_file = aes.encrypt(json.dumps(entries))

with open('{}.ejson'.format(md5(bytes.fromhex(args[3])).hexdigest()), 'wb') as fs:
    fs.write(ret_file)