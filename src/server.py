import json
import passwordJSON
import pyrsa
import random

from pyaes import Rijndael as AES
from os import listdir
from hashlib import md5
from flask import Flask, request, Response, render_template

def resp(text):
    resp = Response(text)
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# initialize application
app = Flask(__name__)

# prepare RSA keys
rsa = pyrsa.RSA_Encryption()

def hashKey(k : bytes) -> str:
    return md5(k).hexdigest()

def checkKey(k):
    fn = hashKey(k)

    missing = True
    for f in listdir('users'):
        if fn in f:
            missing = False
            break

    return missing == False

# /
@app.route('/')
def index():
    return render_template('index.html', r=random.randint(1, 1000))

# /jsrsa.js
@app.route('/jsrsa.js')
def jsrsa():
    # send RSA public key to client
    return render_template('jsrsa.js', 
        rsa_key_n = rsa._key_n, 
        rsa_key_e = rsa._key_e
    )

# /api
@app.route('/api/list', methods = ['POST'])
def computeMessage_list():
    try:
        data = request.get_data(as_text=True)

        # check if any data was sent
        if len(data) == 0:
            return resp(json.dumps({
                'status': 'error', 
                'text': 'Received 0 bytes'
            }))

        # parse json
        data = json.loads(data)

        # decrypt user's AES key
        data['key'] = rsa.decryptKey(data['key'])
        
        # decrypt client's AES key
        data['aes'] = rsa.decryptKey(data['aes'])

        # check if this user's key is valid
        if not checkKey(data['key']):
            return resp(json.dumps({
                'type': 'credentials',
                'status': 'failed'
            }))

        # read passwords file
        l = passwordJSON.read(
            hashKey(data['key']),
            data['key']
        )

        l = json.dumps(l)               # generate string representing given list
        aes = AES(data['aes'])          # load client's AES key
        l = aes.encrypt(l, hex=True)    # encrypt output

        return resp(json.dumps({
            'type': 'list',
            'list': l
        }))
        
    except Exception as e:
        return resp(json.dumps({
            'type': 'error', 
            'text': '{}'.format(e)
        }))

@app.route('/api/details', methods = ['POST'])
def computeMessage_details():
    try:
        data = request.get_data(as_text=True)

        if len(data) == 0:
            return resp(json.dumps({
                'status': 'error', 
                'text': 'Received 0 bytes'
            }))

        data = json.loads(data)

        # decrypt user's AES key
        data['key'] = rsa.decryptKey(data['key'])
        
        # decrypt client's AES key
        data['aes'] = rsa.decryptKey(data['aes'])

        if not checkKey(data['key']):
            return resp(json.dumps({
                'type': 'credentials',
                'status': 'failed'
            }))

        # read passwords file
        el = passwordJSON.read(
            hashKey(data['key']),
            data['key'],
            data['name']
        )

        el = json.dumps(el)               # generate string representing given list
        aes = AES(data['aes'])            # load client's AES key
        el = aes.encrypt(el, hex=True)    # encrypt output
        
        return resp(json.dumps({
            'type': 'details',
            'data': el
        }))

    except Exception as e:
        return resp(json.dumps({
            'type': 'error', 
            'text': '{}'.format(e)
        }))

@app.route('/api/checkCredentials', methods = ['POST'])
def computeMessage_login():
    try:
        data = request.get_data(as_text=True)

        if len(data) == 0:
            return resp(json.dumps({
                'status': 'error', 
                'text': 'Received 0 bytes'
            }))

        data = json.loads(data)

        data['key'] = rsa.decryptKey(data['key'])

        if not checkKey(data['key']):
            return resp(json.dumps({
                'type': 'credentials',
                'status': 'failed'
            }))

        else:     
            return resp(json.dumps({
                'type': 'credentials',
                'status': 'ok'
            }))

    except Exception as e:
        return resp(json.dumps({
            'type': 'error', 
            'text': '{}'.format(e)
        }))

cfg = None
with open('./config.json', 'r') as fs:
    cfg = json.load(fs)

app.run(host=cfg['ip'], port=cfg['port'])