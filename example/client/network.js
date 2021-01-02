class Status {
    static LoggedIn = 1;
    static LoggedOut = 0;

    static shouldLogout = false;
}

HttpClient = {
    request: null,
    status: Status.LoggedOut,

    connect: function(url) {
        HttpClient.request = new XMLHttpRequest();
        HttpClient.request.open('POST', UserData.ip_address + url, true);

        HttpClient.request.onreadystatechange = onMessageEvent;
        HttpClient.request.addEventListener('error', onErrorEvent);
        HttpClient.request.addEventListener('abort', onErrorEvent);
    },

    send: function(text, url) {
        console.log('>>> [' + url + '] ' + text);

        HttpClient.connect(url)
        HttpClient.request.send(text); 
    },

    login: function() {
        HttpClient.send(JSON.stringify({
            'username': UserData.username,
            'pin': UserData.pin
        }), '/api/login');
    },

    list: function() {
        if (HttpClient.status != Status.LoggedIn)
            return;

        HttpClient.send(JSON.stringify({
            'username': UserData.username,
            'password': UserData.password,
            'pin': UserData.pin
        }), '/api/list');
    },

    details: function(name) {
        if (HttpClient.status != Status.LoggedIn)
            return;

        HttpClient.send(JSON.stringify({
            'username': UserData.username,
            'password': UserData.password,
            'pin': UserData.pin,
            'name': name
        }), '/api/details');
    }
}

function onMessageEvent(e) {
    if (HttpClient.request.readyState == 4 && HttpClient.request.status == 200)
    {
        try {
            console.log('<<< ' + HttpClient.request.responseText);

            let data = JSON.parse(HttpClient.request.responseText);
        
            switch(data['type']) 
            {
                case 'login':
                    Status.shouldLogout = false;

                    if (data['status'] == 'ok')
                        HttpClient.status = Status.LoggedIn;
                    else
                        HttpClient.status = Status.LoggedOut;
                        
                    break;

                case 'list':
                    GUI.clearList();

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
}

function onErrorEvent(e) {
    console.log(e);
}
