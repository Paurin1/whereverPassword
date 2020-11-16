let last_status = -1;
let tick_count = 0;

function loop() {
    if (HttpClient.status != last_status) {
        GUI.applyStatus();

        if (HttpClient.status == Status.LoggedIn) {
            HttpClient.list();
        } else {
            GUI.hideDetails();
            GUI.clearList();
        }

        last_status = HttpClient.status;
    }

    // validate PIN every 4 seconds
    if (HttpClient.status == Status.LoggedIn && tick_count % 4 == 0) {
        Status.shouldLogout = true;
        
        HttpClient.login();
    }

    // check if login request resolved in time (1 second)
    if (Status.shouldLogout == true && tick_count % 4 == 1) {
        HttpClient.status = Status.LoggedOut;

        GUI.hideDetails();
        GUI.clearList();
    }

    ++tick_count;
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
        if (HttpClient.status == Status.LoggedIn) {
            document.getElementsByClassName('notification-disconnected')[0].style.visibility = 'hidden';
            document.getElementsByClassName('notification-connected')[0].style.visibility = 'hidden';
        } else {
            document.getElementsByClassName('notification-disconnected')[0].style.visibility = 'hidden';
            document.getElementsByClassName('notification-connected')[0].style.visibility = 'visible';
            GUI.hideDetails();
        }
    },

    requestDetails: function(caller) {
        HttpClient.details(caller.innerHTML);
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
            UserData.pin = final;
            HttpClient.login();
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

setInterval(loop, 1000);