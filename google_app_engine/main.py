import json
import pyrsa
import pyaes

# there is a corresponding read function for *.kdbx files
# but for now I just leave it as it is
import pwd_ejson as pwds
# import pwd_kdbx as pwds

from keygen import hashKey
from os.path import exists
from hashlib import md5
from flask import Flask, request, render_template

# config
_IP = '0.0.0.0'
_PORT = 65432

def checkKey(k):
    return exists('users/{}.ejson'.format(hashKey(k)))

# prepare RSA keys
rsa = pyrsa.RSA_Encryption()

# create Flask application
app = Flask(__name__)

# /
@app.route('/')
def index():
    return render_template('index.html')

# /rsa.js
@app.route('/rsa.js')
def jsrsa():
    # send RSA public key to the client
    return render_template('rsa.js', 
        rsa_key_n = rsa.key_n, 
        rsa_key_e = rsa.key_e
    )

# /api
@app.route('/api/list', methods = ['POST'])
def api_list():
    try:
        # force=True allows text/plain to be parsed as JSON
        data = request.get_json(force=True)

        # decrypt AES master key
        data['key'] = rsa.decryptKey(data['key'])
        
        # decrypt AES key that will be used for communication
        data['aes'] = rsa.decryptKey(data['aes'])

        # check if this master key is valid
        if not checkKey(data['key']):
            return json.dumps({
                'type': 'credentials',
                'status': 'failed'
            })

        # read passwords list
        l = pwds.read(
            hashKey(data['key']),   # user's file name
            data['key']             # master key
        )

        l = json.dumps(l)               # generate JSON string representing given list
        aes = pyaes.Rijndael(data['aes'])          # load client's AES key
        l = aes.encrypt(l, hex=True)    # encrypt output

        return json.dumps({
            'type': 'list',
            'list': l
        })
        
    except Exception as e:
        return json.dumps({
            'type': 'error', 
            'text': '{}'.format(e)
        })

@app.route('/api/details', methods = ['POST'])
def api_details():
    try:
        data = request.get_json(force=True)

        data['key'] = rsa.decryptKey(data['key'])
        data['aes'] = rsa.decryptKey(data['aes'])

        if not checkKey(data['key']):
            return json.dumps({
                'type': 'credentials',
                'status': 'failed'
            })

        # read details on entry data['name']
        el = pwds.read(
            hashKey(data['key']),
            data['key'],
            data['name']
        )

        el = json.dumps(el)               # generate JSON string representing output
        aes = pyaes.Rijndael(data['aes'])            # load client's AES key
        el = aes.encrypt(el, hex=True)    # encrypt output
        
        return json.dumps({
            'type': 'details',
            'data': el
        })

    except Exception as e:
        return json.dumps({
            'type': 'error', 
            'text': '{}'.format(e)
        })

@app.route('/api/checkCredentials', methods = ['POST'])
def api_checkCredentials():
    try:
        data = request.get_json(force=True)

        data['key'] = rsa.decryptKey(data['key'])

        if not checkKey(data['key']):
            return json.dumps({
                'type': 'credentials',
                'status': 'failed'
            })

        else:     
            return json.dumps({
                'type': 'credentials',
                'status': 'ok'
            })

    except Exception as e:
        return json.dumps({
            'type': 'error', 
            'text': '{}'.format(e)
        })

if __name__ == '__main__':
    print('Running app at port {}'.format(_PORT))
    app.run(host=_IP, port=_PORT)