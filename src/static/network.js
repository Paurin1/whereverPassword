HttpClient = {
    request: null,

    connect: function(url) {
        HttpClient.request = new XMLHttpRequest();
        HttpClient.request.onreadystatechange = onMessageEvent;
        HttpClient.request.addEventListener('error', onErrorEvent);
        HttpClient.request.addEventListener('abort', onErrorEvent);

        HttpClient.request.open('POST', document.URL + url, true);
    },

    send: function(text, url) {
        console.log('>>> [' + url + '] ' + text);

        HttpClient.connect(url)
        HttpClient.request.send(text); 
    },

    list: function() {
        HttpClient.send(JSON.stringify({
            'key': Cookies.get('key'),
            'aes': session_key_enc
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
            'aes': session_key_enc,
            'name': name
        }), 'api/details');
    }
}

function onMessageEvent(e) {
    if (HttpClient.request.readyState != 4 || HttpClient.request.status != 200)
        return;

    try {
        console.log('<<< ' + HttpClient.request.responseText);

        let recv = JSON.parse(HttpClient.request.responseText);
    
        switch(recv['type']) 
        {
            case 'credentials':
                if (recv['status'] == 'ok') {
                    GUI.hideKey();
                    HttpClient.list();
                } else {
                    GUI.enterKey();
                }
                break;

            case 'list':
                GUI.clearList();

                // decrypt received data
                aes = new AES.init(AES.utils.hex.toBytes(session_key))
                recv['list'] = AES.utils.utf8.fromBytes(aes.decryptData(AES.utils.hex.toBytes(recv['list'])));
                recv['list'] = JSON.parse(recv['list']);

                for (let i = 0; i < recv['list'].length; ++i) {
                    GUI.addElement(
                        recv['list'][i]['name'],
                        recv['list'][i]['url']
                    );
                }
                break;
    
            case 'details':
                // decrypt received data
                aes = new AES.init(AES.utils.hex.toBytes(session_key))
                recv['data'] = AES.utils.utf8.fromBytes(aes.decryptData(AES.utils.hex.toBytes(recv['data'])));
                recv['data'] = JSON.parse(recv['data']);

                GUI.showDetails(
                    recv['data']['name'],
                    recv['data']['username'],
                    window.atob(recv['data']['password']),
                    recv['data']['url']
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

function onErrorEvent(e) {
    console.log(e);
}
