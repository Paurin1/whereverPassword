import base64
import json
import pyaes
import sys
import keygen

from os import path

# usage:
# python ffcsv2ejson.py [csv file] [hex key]
args = sys.argv

# check if it is a keyfile or password

# read all entries from this csv file
entries = {}
with open(args[1], 'r') as fs:
    # localize url, username and password positions
    tag_line = fs.readline()
    url_pos = tag_line.split(',').index('"url"')
    usr_pos = tag_line.split(',').index('"username"')
    pas_pos = tag_line.split(',').index('"password"')
    
    for line in fs.readlines()[1:]:
        values = [v.strip('"') for v in line.split(',')]
        url = values[url_pos]
        username = values[usr_pos]
        password = values[pas_pos]

        # these entries does not have names
        # so we need to generate ones that are unique
        hash = keygen.md5(url.encode('utf-8') + username.encode('utf-8')).hexdigest()
        name = 'firefox_' + ''.join([c for i, c in enumerate(hash) if i % 4 == 0])

        entries[name] = {
            'name': name,
            'url': url,
            'username': username,
            'password': base64.b64encode(password.encode('utf-8')).decode('ascii')
        }

# if a key was specified then use it
if len(args) == 3:
    key = bytes.fromhex(args[2])
    aes = pyaes.Rijndael(key)

# otherwise generate new key and display it afterwards
else:
    key = keygen.get_bytes()
    aes = pyaes.Rijndael(key)
    print(hex(key)[2:])

# generate output file name
fn = keygen.hashKey(key)

# if file exists -> load it and update it's content
if path.exists('{}.ejson'.format(fn)):
    file_entries = aes.decrypt(open('{}.ejson'.format(fn), 'rb').read())
    file_entries = json.loads(file_entries)

    file_entries.update(entries)

    entries_dump = aes.encrypt(json.dumps(file_entries))

    with open('{}.ejson'.format(fn), 'wb') as fs:
        fs.write(entries_dump)

# if file does not exists -> simply create it and dump the data
else:
    # dump all entries and encrypt them
    entries_dump = aes.encrypt(json.dumps(entries))

    # save encrypted entries to a file named with a MD5 hash of a password
    with open('{}.ejson'.format(fn), 'wb') as fs:
        fs.write(entries_dump)