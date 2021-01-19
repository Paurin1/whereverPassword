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

        document.getElementById('entryContainer').addElement(elem);
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

// initials
GUI.clearList();
GUI.hideDetails();

// check if key is saved in cookies
if (typeof Cookies.get('key') === 'undefined') {
    // display key textboxes
    GUI.enterKey();
} else {
    GUI.hideKey();
}