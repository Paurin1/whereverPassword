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
        document.getElementById('entryURL').href = url == null ? '' : url;
        document.getElementById('entryURL').innerHTML = url;
        document.getElementById('entryUsername').innerHTML = username;
        document.getElementById('entryPassword').innerHTML = password;
        
        document.getElementById('copyusername').value = username;
        document.getElementById('copypassword').value = password;
    },

    addElement: function(name, url) {
        if (typeof url === 'undefined')
            url = '-';

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

        MasterKey.clear();

        document.getElementById('masterKeyWrapper').style.display = 'flex';
    },

    hideKey: function() {
        GUI.hideCurtain();

        document.getElementById('masterKeyWrapper').style.display = 'none';
    },

    copyUsername: function() {
        copyToClipboard('copyusername');
    },

    copyPassword: function() {
        copyToClipboard('copypassword');
    },

    copyUrl: function() {
        copyToClipboard('copyurl');
    },

    curtainClick: function() {
        if (typeof Cookies.get('key') === 'undefined')
            return;

        GUI.hideDetails();
    }
}