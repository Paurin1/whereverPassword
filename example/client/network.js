class Status {
    static Disconnected = 0;
    static Connected = 1;
    static LoggedIn = 3;
}

SocketClient = {
    socket: null,
    status: Status.Disconnected,

    connect: function() {
        SocketClient.socket = new WebSocket("ws://127.0.0.1:65432");

        SocketClient.socket.onopen = onOpenEvent;
        SocketClient.socket.onmessage = onMessageEvent;
        SocketClient.socket.onclose = onCloseEvent;
        SocketClient.socket.onerror = onErrorEvent;    
    },

    send: function(text) {
        console.log('>>> ' + text);

        SocketClient.socket.send(text);
    },

    login: function(pin) {
        SocketClient.send(JSON.stringify({
            'command': 'login',
            'username': UserData.username,
            'pin': pin
        }));
    },

    list: function() {
        if (SocketClient.status != Status.LoggedIn)
            return;

        SocketClient.send(JSON.stringify({
            'command': 'list',
            'username': UserData.username,
            'password': UserData.password
        }));
    },

    details: function(name) {
        if (SocketClient.status != Status.LoggedIn)
            return;

        SocketClient.send(JSON.stringify({
            'command': 'details',
            'username': UserData.username,
            'password': UserData.password,
            'name': name
        }));
    }
}

function onOpenEvent(e) {
    SocketClient.status = Status.Connected;
    console.log('Connected');
}

function onMessageEvent(e) {
    console.log('<<< ' + e.data);

    try {
        let data = JSON.parse(e.data);
    
        switch(data['type']) 
        {
            case 'loggedin':
                SocketClient.status = Status.LoggedIn;
                SocketClient.list();
                break;
    
            case 'list':
                for (let i = 0; i < data['list'].length; ++i) {
                    GUI.addElement(
                        data['list'][i]['name']
                    );
                }
                break;
    
            case 'details':
                GUI.showDetails(
                    data['data']['name'],
                    data['data']['username'],
                    window.atob(data['data']['password'])
                );
                break;
    
            default:
                break;
        }

    } catch(e) {
        console.log(e);
        return;
    }
}

function onCloseEvent(e) {
    SocketClient.status = Status.Disconnected;
    console.log('Disconnected');
}

function onErrorEvent(e) {
    SocketClient.status = Status.Disconnected;
    console.log('Dropped');
    console.log(e);
}
