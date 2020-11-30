import json
import pathlib
import base64

import pyaes
from pykeepass import PyKeePass
from flask import Flask, request, Response

# pin is not used for now
def readKeePass(username, password, name=None):
    password = base64.b64decode(password)

    # modified pykeepass.kdbx_parsing.common line 110
    kp = PyKeePass('{}.kdbx'.format(username), password=password)
    gr = kp.root_group

    if name:
        for entry in gr.entries:
            if entry.title == name:
                return {
                    'name': entry.title,
                    'username': entry.username,
                    'password': base64.b64encode(entry.password.encode('utf-8')).decode('ascii'),
                    'url': entry.url
                }

    else:
        ret_list = []

        for entry in gr.entries:
            ret_list.append({
                'name': entry.title,
                'url': entry.url
            })

        return ret_list

def resp(text):
    resp = Response(text)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'POST'
    return resp

def encryptMessage(message: bytes, username):
    with open('pins.json', 'r') as fs:
        pins = json.load(fs)
        for pin in pins:
            if pin['username'] == username:
                r = pyaes.Rijndael(pin['aes_key'])
                return r.encrypt(message)

def decryptMessage(message: bytes, username):
    with open('pins.json', 'r') as fs:
        pins = json.load(fs)
        for pin in pins:
            if pin['username'] == username:
                r = pyaes.Rijndael(pin['aes_key'])
                return r.decrypt(message)

app = Flask(__name__)

@app.route('/api/list', methods = ['POST'])
def computeMessage_list():
    try:
        data = request.get_data()

        if len(data) == 0:
            return resp(json.dumps({
                'type': 'error', 
                'text': 'Received 0 bytes'
            }))

        m = json.loads(data)

        l = readKeePass(
            m['username'],
            decryptMessage(m['password'], m['username'])
        )

        return resp(json.dumps({
            'type': 'list',
            'list': encryptMessage(json.dumps(l), m['username'])
        }))
        
    except Exception as e:
        return resp(json.dumps({
            'type': 'error', 
            'text': '{}'.format(e)
        }))

@app.route('/api/details', methods = ['POST'])
def computeMessage_details():
    try:
        data = request.get_data()

        if len(data) == 0:
            return resp(json.dumps({
                'type': 'error', 
                'text': 'Received 0 bytes'
            }))

        m = json.loads(data)

        el = readKeePass(
            m['username'],
            decryptMessage(m['password'], m['username']),
            m['name']
        )
        
        return resp(json.dumps({
            'type': 'details',
            'data': encryptMessage(json.dumps(el), m['username'])
        }))

    except Exception as e:
        return resp(json.dumps({
            'type': 'error', 
            'text': '{}'.format(e)
        }))

@app.route('/api/login', methods = ['POST'])
def computeMessage_login():
    try:
        data = request.get_data()

        if len(data) == 0:
            return resp(json.dumps({
                'type': 'error', 
                'text': 'Received 0 bytes'
            }))

        m = json.loads(data)

        with open('pins.json', 'r') as fs:
            pins = json.load(fs)
            for pin in pins:
                if pin['username'] == m['username'] and pin['pin'] == m['pin']:
                    return resp(json.dumps({
                        'type': 'login',
                        'status': 'ok'
                    }))
                    
        return resp(json.dumps({
                'type': 'login',
                'status': 'failed'
            }))

    except Exception as e:
        return resp(json.dumps({
            'type': 'error', 
            'text': '{}'.format(e)
        }))

cfg = None
with open('config.json', 'r') as fs:
    cfg = json.load(fs)

app.run(host=cfg['ip'], port=cfg['port'])