import json
import passwordJSON

from flask import Flask, request, Response

def resp(text):
    resp = Response(text)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
    
app = Flask(__name__)

@app.route('/api/list', methods = ['POST'])
def computeMessage_list():
    try:
        data = request.get_data()

        # for backwards compatibility (i.e. Raspbian)
        if type(data) is bytes:
            data = data.decode('ascii')

        if len(data) == 0:
            return resp(json.dumps({
                'type': 'error', 
                'text': 'Received 0 bytes'
            }))

        m = json.loads(data)

        print(m['password'])

        l = passwordJSON.read(
            m['username'],
            m['password']
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

        # for backwards compatibility (i.e. Raspbian)
        if type(data) is bytes:
            data = data.decode('ascii')

        if len(data) == 0:
            return resp(json.dumps({
                'type': 'error', 
                'text': 'Received 0 bytes'
            }))

        m = json.loads(data)

        el = passwordJSON.read(
            m['username'],
            m['password'],
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

        # for backwards compatibility (i.e. Raspbian)
        if type(data) is bytes:
            data = data.decode('ascii')

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
with open('./config.json', 'r') as fs:
    cfg = json.load(fs)

app.run(host=cfg['ip'], port=cfg['port'], debug=True)