import json
import pathlib
import base64

from pykeepass import PyKeePass
from flask import Flask, request, Response

# pin is not used for now
def readKeePass(username, password, pin, name=None):
    password = base64.b64decode(bytes(password, 'ascii'))

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
    return resp
    
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
            m['password'],
            m['pin']
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
        data = request.get_data()

        if len(data) == 0:
            return resp(json.dumps({
                'type': 'error', 
                'text': 'Received 0 bytes'
            }))

        m = json.loads(data)

        el = readKeePass(
            m['username'],
            m['password'],
            m['pin'],
            m['name']
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

app.run(host=cfg['ip'], port=cfg['port'], debug=True)