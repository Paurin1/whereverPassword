function copyToClipboard(id) {
    let dom = document.getElementById(id);
    dom.style.display = 'block';
    dom.select();
    document.execCommand('copy');
    dom.style.display = 'none';
}

GUI = {
    requestDetails: function() {
        HttpClient.details(this.id);
    },

    hideDetails: function() {
        GUI.hideCurtain();
        document.getElementById('details').style.display = 'none';

        document.getElementById('entryName').innerHTML = '';
        document.getElementById('entryURL').href = '#';
        document.getElementById('entryURL').innerHTML = '';
        document.getElementById('entryUsername').innerHTML = '';
        document.getElementById('entryPassword').innerHTML = '';
        
        document.getElementById('copyusername').value = '';
        document.getElementById('copypassword').value = '';
    },

    showDetails: function(name, username, password, url) {
        GUI.showCurtain();
        document.getElementById('details').style.display = 'block';
        
        document.getElementById('entryName').innerHTML = name;
        document.getElementById('entryURL').href = url;
        document.getElementById('entryURL').innerHTML = url;
        document.getElementById('entryUsername').innerHTML = username;
        document.getElementById('entryPassword').innerHTML = password;
        
        document.getElementById('copyusername').value = username;
        document.getElementById('copypassword').value = password;
    },

    addElement: function(name, url) {
        let elem = document.createElement('div');
        elem.id = name;
        elem.className = 'entry';
        elem.innerHTML = `${name} [${url}]`;
        elem.addEventListener('click', GUI.requestDetails);

        document.getElementById('entryContainer').appendChild(elem);
    },

    clearList: function() {
        document.getElementById('entryContainer').innerHTML = '';
    },

    hideCurtain: function() {
        document.getElementById('curtain').style.display = 'none';
    },

    showCurtain: function() {
        document.getElementById('curtain').style.display = 'block';
    },

    enterKey: function() {
        GUI.clearList();
        GUI.hideDetails();
        GUI.showCurtain();

        Register.clear();

        document.getElementById('registerWrapper').style.display = 'flex';
    },

    hideKey: function() {
        GUI.hideCurtain();

        document.getElementById('registerWrapper').style.display = 'none';
    },

    copyUsername: function() {
        copyToClipboard('copyusername');
    },

    copyPassword: function() {
        copyToClipboard('copypassword');
    },

    curtainClick: function() {
        if (typeof Cookies.get('key') === 'undefined')
            return;

        GUI.hideDetails();
    }
}

// set event handlers
document.getElementById('entryUsername').addEventListener('click', GUI.copyUsername);
document.getElementById('entryPassword').addEventListener('click', GUI.copyPassword);
document.getElementById('curtain').addEventListener('click', GUI.curtainClick);
for (let i = 0; i < 8; ++i) {
    Register.textboxes[i].addEventListener('input', Register.onChange);
    Register.textboxes[i].addEventListener('keyup', Register.onKeyUp);
}

// initials
GUI.clearList();
GUI.hideDetails();

// create AES-key for communication
Register.generateAesKey();

// check if any cookie is missing
if (typeof Cookies.get('key') === 'undefined' || typeof Cookies.get('rsa') === 'undefined') {
    // display key textboxes
    GUI.enterKey();
} else {
    // check if RSA key is the same as the one from server
    if (Cookies.get('rsa') == RSA.pk_n) {
        GUI.hideKey();
        HttpClient.list();
    } else {
        GUI.enterKey();
    }
}