import asyncio
import websockets
import json
import pathlib
import base64

from pykeepass import PyKeePass

async def readKeePass(username, password, name=None):
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

async def computeMessage(websocket, message):
    response = ''
    
    try:
        m = json.loads(message)

        if m['command'] == 'list':
            l = await readKeePass(
                m['username'],
                m['password']
            )

            response = json.dumps({
                'type': 'list',
                'list': l
            })

        elif m['command'] == 'details':
            el = await readKeePass(
                m['username'],
                m['password'],
                m['name']
            )
            
            response = json.dumps({
                'type': 'details',
                'data': el
            })

        else:
            response = json.dumps({'type': 'error', 'text': 'command not recognized'})

    except Exception as e:
        response = json.dumps({'type': 'error', 'text': e})

    await websocket.send(response)

async def checkLogin(message):
    message = json.loads(message)

    with open('pins.json', 'r') as fs:
        pins = json.load(fs)
        for pin in pins:
            if pin['username'] == message['username'] and pin['pin'] == message['pin']:
                return True
    return False

async def connect(websocket, path):
    print('New connection')

    async for message in websocket:
        try:
            if await checkLogin(message) == False:
                print('Invalid credentials')
                return
            else:
                await websocket.send(json.dumps({'type': 'loggedin'}))
            
            async for message in websocket:
                await computeMessage(websocket, message)

        finally:
            print('Finished connection')

def startServer(ip='0.0.0.0', port=65432):
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(connect, ip, port)
    )

    asyncio.get_event_loop().run_forever()

cfg = None
with open('config.json', 'r') as fs:
    cfg = json.load(fs)

startServer(ip=cfg['ip'], port=cfg['port'])