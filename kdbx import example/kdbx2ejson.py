import base64
import json
import pyaes
import sys
import keygen

from os import path
from pykeepass import PyKeePass

# usage:
# python kdbx2ejson.py [kdbx file] [key file / password] [hex key]
args = sys.argv

# check if it is a keyfile or password
kf = None; pwd = None
if path.exists(args[2]):
    kf = args[2]
else:
    pwd = args[2]

kp = PyKeePass(args[1], keyfile=kf, password=pwd)

# read all entries from this kdbx file
entries = []
for entry in kp.entries:
    entries.append({
        'name': entry.title,
        'url': entry.url,
        'username': entry.username,
        'password': base64.b64encode(entry.password.encode('utf-8')).decode('ascii')
    })

# if a key was specified then use it
if len(args) == 4:
    aes = pyaes.Rijndael(bytes.fromhex(args[3]))

# otherwise generate new key and display it afterwards
else:
    key = keygen.get_bytes()
    aes = pyaes.Rijndael(base64.b64decode(key))
    print(key)

# dump all entries and encrypt them
ret_file = aes.encrypt(json.dumps(entries))

# save encrypted entries to a file named with a MD5 hash of a password
with open('{}.ejson'.format(keygen.hashKey(bytes.fromhex(args[3]))), 'wb') as fs:
    fs.write(ret_file)