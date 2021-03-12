// some function from stackoverflow to copy some text into clipboard
function copyToClipboard(id) {
    let dom = document.getElementById(id);
    dom.style.display = 'block';
    dom.select();
    document.execCommand('copy');
    dom.style.display = 'none';
}

// set event handlers
document.getElementById('entryUsername').addEventListener('click', GUI.copyUsername);
document.getElementById('entryPassword').addEventListener('click', GUI.copyPassword);
document.getElementById('entryURL').addEventListener('click', GUI.copyUrl);
document.getElementById('curtain').addEventListener('click', GUI.curtainClick);
for (let i = 0; i < 8; ++i) {
    MasterKey.textboxes[i].addEventListener('input', MasterKey.onChange);
    MasterKey.textboxes[i].addEventListener('keyup', MasterKey.onKeyUp);
}

// initials
GUI.clearList();
GUI.hideDetails();

// create AES-key for decrypting messages from server
const session_key = AES.utils.hex.fromBytes(window.crypto.getRandomValues(new Uint8Array(16)));
const session_key_enc = RSA.encrypt(session_key);

// check if any cookie is missing
if (typeof Cookies.get('key') === 'undefined' || typeof Cookies.get('rsa') === 'undefined') {
    // display master key textboxes
    GUI.enterKey();
} else {
    // check if RSA key is the same as the one received from server
    if (Cookies.get('rsa') == RSA.pk_n) {
        GUI.hideKey();
        HttpClient.list();
    } else {
        // if keys vary then the user needs to enter the master key once again because we need to encrypt it with the new RSA key
        GUI.enterKey();
    }
}