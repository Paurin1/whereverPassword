HttpClient = {
    request: null,

    connect: function(url) {
        HttpClient.request = new XMLHttpRequest();
        HttpClient.request.open('POST', document.URL + url, true);

        HttpClient.request.onreadystatechange = onMessageEvent;
        HttpClient.request.addEventListener('error', onErrorEvent);
        HttpClient.request.addEventListener('abort', onErrorEvent);
    },

    send: function(text, url) {
        console.log('>>> [' + url + '] ' + text);

        HttpClient.connect(url)
        HttpClient.request.send(text); 
    },

    list: function() {
        HttpClient.send(JSON.stringify({
            'key': Cookies.get('key')
        }), 'api/list');
    },

    credentials: function() {
        HttpClient.send(JSON.stringify({
            'key': Cookies.get('key')
        }), 'api/checkCredentials');
    },

    details: function(name) {
        HttpClient.send(JSON.stringify({
            'key': Cookies.get('key'),
            'name': name
        }), 'api/details');
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
                case 'credentials':
                    if (data['status'] == 'ok') {
                        GUI.hideKey();
                        HttpClient.list();
                    } else {
                        GUI.enterKey();
                    }
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
