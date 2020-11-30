import sys
import json

def error(text=None):
    print('\tInvalid syntax: configure.py [server/client] -[i/p/np]')
    if text:
        print(text)
    print('\t-i: IP address')
    print('\t-p: port')
    print('\t-np: new PIN for a user, usage: USER/PIN')
    exit()

def port(num):
    if num.isnumeric() == False:
        error('Port must be numeric')

    n = int(num)

    cfg = None
    with open('src/server/config.json', 'r') as fs:
        cfg = json.load(fs)

    cfg['port'] = n

    with open('src/server/config.json', 'w') as fs:
        json.dump(cfg, fs)


def ip(num):
    # validate
    gr = num.split('.')
    if len(gr) != 4:
        error('IP should look like 000.000.000.000')
    for g in gr:
        if g.isnumeric() is False:
            error('IP should look like 000.000.000.000')

    cfg = None
    with open('src/server/config.json', 'r') as fs:
        cfg = json.load(fs)

    cfg['ip'] = num

    with open('src/server/config.json', 'w') as fs:
        json.dump(cfg, fs)

def setclientipport(ip=None, port=None):
    raw = None
    with open('src/client/network.js', 'r+') as fs:
        raw = fs.read()

        ws_pos = raw.find('new WebSocket') + len('new WebSocket') + 7
        ws_end = raw.find('"', ws_pos)

        _ip, _port = raw[ws_pos:ws_end].split(':')

        if not ip:
            ip = _ip

        if not port:
            port = _port

        raw = raw.replace(raw[ws_pos:ws_end], '{}:{}'.format(ip, port))

    with open('src/client/network.js', 'w') as fs:
        fs.write(raw)

def serverip(num):
    # validate
    gr = num.split('.')
    if len(gr) != 4:
        error('IP should look like 000.000.000.000')
    for g in gr:
        if g.isnumeric() is False:
            error('IP should look like 000.000.000.000')

    setclientipport(ip=num)

def serverport(num):
    if num.isnumeric() == False:
        error('Port must be numeric')

    setclientipport(port=num)

def newpin(pin):
    up = pin.split('/')

    if len(up) != 2:
        error('new PIN should look like USERNAME/0000')

    if up[0].isalnum() is False or up[1].isnumeric() is False:
        error('new PIN should look like USERNAME/0000')

    cfg = None
    with open('src/server/pins.json', 'r') as fs:
        cfg = json.load(fs)

    cfg.append({'username': up[0], 'pin': up[1]})
        
    with open('src/server/pins.json', 'w') as fs:
        json.dump(cfg, fs)

if len(sys.argv) < 3:
    error()

import secrets
import base64
if sys.argv[1] == 'newkey':
    print(base64.b64encode(secrets.token_bytes(int(sys.argv[2]))).decode('ascii'))
    exit()

if len(sys.argv) < 4:
    error()

if sys.argv[1] == 'server':
    if len(sys.argv) % 2 != 0:
        error()

    for i in range(int((len(sys.argv)-2)/2)):
        tag = sys.argv[2+i*2]
        value = sys.argv[2+i*2+1]

        if tag == '-i':
            ip(value)

        elif tag == '-p':
            port(value)

        elif tag == '-np':
            newpin(value)

elif sys.argv[1] == 'client':
    if len(sys.argv) % 2 != 0:
        error()

    for i in range(int((len(sys.argv)-2)/2)):
        tag = sys.argv[2+i*2]
        value = sys.argv[2+i*2+1]

        if tag == '-i':
            serverip(value)

        elif tag == '-p':
            serverport(value)

else:
    error()