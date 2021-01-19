import json
import passwordJSON

from os import listdir
from hashlib import md5
from flask import Flask, request, Response, render_template

def resp(text):
    resp = Response(text)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

app = Flask(__name__)

def hashKey(k):
    return md5(bytes.fromhex(k)).hexdigest()

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
    return render_template('index.html')

# /api
@app.route('/api/list', methods = ['POST'])
def computeMessage_list():
    try:
        data = request.get_data(as_text=True)

        if len(data) == 0:
            return resp(json.dumps({
                'status': 'error', 
                'text': 'Received 0 bytes'
            }))

        data = json.loads(data)

        if not checkKey(data['key']):
            return resp(json.dumps({
                'type': 'credentials',
                'status': 'failed'
            }))

        l = passwordJSON.read(
            hashKey(data['key']),
            data['key']
        )

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

        if not checkKey(data['key']):
            return resp(json.dumps({
                'type': 'credentials',
                'status': 'failed'
            }))

        el = passwordJSON.read(
            hashKey(data['key']),
            data['key'],
            data['name']
        )
        
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