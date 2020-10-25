let last_status = -1;

function loop() {
    // this might cause problems when trying to reconnect by blocking the action from repeating
    if (SocketClient.status == last_status)
        return;

    GUI.applyStatus();

    if (SocketClient.status == Status.Disconnected)
        SocketClient.connect();
}

function copyToClipboard(id) {
    let dom = document.getElementById(id);
    dom.style.display = 'block';
    dom.select();
    document.execCommand('copy');
    dom.style.display = 'none';
}

GUI = {
    applyStatus: function() {
        switch(SocketClient.status)
        {
            case Status.Disconnected:
                document.getElementsByClassName('notification-disconnected')[0].style.visibility = 'visible';
                document.getElementsByClassName('notification-connected')[0].style.visibility = 'hidden';
                GUI.hideDetails();
                GUI.clearList();
                break;

            case Status.Connected:
                document.getElementsByClassName('notification-disconnected')[0].style.visibility = 'hidden';
                document.getElementsByClassName('notification-connected')[0].style.visibility = 'visible';
                GUI.hideDetails();
                break;

            case Status.LoggedIn:
                document.getElementsByClassName('notification-disconnected')[0].style.visibility = 'hidden';
                document.getElementsByClassName('notification-connected')[0].style.visibility = 'hidden';
                break;
        }
    },

    requestDetails: function(caller) {
        SocketClient.details(caller.innerHTML);
    },

    validatePIN: function() {
        let pin_textbox = document.getElementById('pin'); 
        let pin = pin_textbox.value;
    
        let final = '';
    
        if (pin.length <= 4) {
            for (let i = 0; i < 4 && i < pin.length; ++i) {
                if (
                    pin[i] == '1' ||
                    pin[i] == '2' ||
                    pin[i] == '3' ||
                    pin[i] == '4' ||
                    pin[i] == '5' ||
                    pin[i] == '6' ||
                    pin[i] == '7' ||
                    pin[i] == '8' ||
                    pin[i] == '9' ||
                    pin[i] == '0' 
                ) final += pin[i];
    
                else {
                    break;
                }
            }  
        }
    
        if (final.length == 4) {
            SocketClient.login(final);
        }

        pin_textbox.value = final;
    },

    hideDetails: function() {
        document.getElementsByClassName('notification-details')[0].style.visibility = 'hidden';
    
        document.getElementById('name').innerHTML = '';
        document.getElementById('username').innerHTML = '';
        document.getElementById('password').innerHTML = '';
        
        document.getElementById('copyusername').value = '';
        document.getElementById('copypassword').value = '';
    },

    showDetails: function(name, username, password) {
        let det = document.getElementsByClassName('notification-details')[0];
        det.style.visibility = 'visible';
    
        document.getElementById('name').innerHTML = name;
        document.getElementById('username').innerHTML = username;
        document.getElementById('password').innerHTML = password;
        
        document.getElementById('copyusername').value = username;
        document.getElementById('copypassword').value = password;
    },

    addElement: function(name) {
        document.getElementsByClassName('container')[0].innerHTML 
            += "<div class='element' onclick='GUI.requestDetails(this)'>"
            + name + "</div>";
    },

    clearList: function() {
        document.getElementsByClassName('container')[0].innerHTML = '';
    }
}

setInterval(loop, 250);