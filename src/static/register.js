Register = {
    // number of days that cookie is stored
    cookie_expiration: 7,

    textboxes: [
        document.getElementById('g1'),
        document.getElementById('g2'),
        document.getElementById('g3'),
        document.getElementById('g4'),
        document.getElementById('g5'),
        document.getElementById('g6'),
        document.getElementById('g7'),
        document.getElementById('g8')
    ],

    generateAesKey() {
        Register.session_key = AES.utils.hex.fromBytes(window.crypto.getRandomValues(new Uint8Array(16)))
        Register.session_key_enc = RSA.encrypt(Register.session_key);
        
        console.log(Register.session_key);
        console.log(Register.session_key_enc);
    },

    getKey: function() {
        let alnum = '';
        for (let i = 0; i < 8; ++i) {
            alnum += Register.textboxes[i].value[0];
            alnum += Register.textboxes[i].value[2];
            alnum += Register.textboxes[i].value[4];
            alnum += Register.textboxes[i].value[6];
        }
        return alnum.toLowerCase();
    },

    isReady: function() {
        // check lengths
        for (let i = 0; i < 8; ++i) {
            if (Register.textboxes[i].value.length != 7)
                return false;
    
            if (Register.textboxes[i].value[1] != ' ' ||
                Register.textboxes[i].value[3] != ' ' ||
                Register.textboxes[i].value[5] != ' ')
                return false;
        }
    
        return true;
    },

    isAlnum: function(c) {
        if ((48 > c || c > 57) && (65 > c || c > 70) && (97 > c || c > 102))
            return false;
    
        return true;
    },

    onChange: function() {
        // extract alnum
        let alnum = [];
        for (let i = 0; i < this.value.length; ++i) {
            if (Register.isAlnum(this.value.charCodeAt(i)))
                alnum.push(this.value[i]);
    
            // limit to only 4 chars
            if (alnum.length == 4)
                break;
        }
    
        // add spaced in between
        this.value = alnum.join(' ');
        
        // check if it is worth validating key
        if (alnum.length == 4)
            if (Register.isReady())
                Register.apply();
    
            // change focus
            else {
                switch(this.id) {
                    case 'g1': Register.textboxes[1].focus(); break;
                    case 'g2': Register.textboxes[2].focus(); break;
                    case 'g3': Register.textboxes[3].focus(); break;
                    case 'g4': Register.textboxes[4].focus(); break;
                    case 'g5': Register.textboxes[5].focus(); break;
                    case 'g6': Register.textboxes[6].focus(); break;
                    case 'g7': Register.textboxes[7].focus(); break;
                    case 'g8': Register.textboxes[0].focus(); break;
                }
            }
    },

    onKeyUp: function(e) {
        if (e.keyCode === 13) {
            if (Register.isReady())
                Register.apply();
        }
    },

    setKeyCookie: function() {
        let key = Register.getKey();
        let enc_key = RSA.encrypt(key);

        Cookies.set('key', enc_key, { expires: Register.cookie_expiration });
        Cookies.set('rsa', RSA.pk_n, { expires: Register.cookie_expiration });
    },

    apply: function() {
        Register.setKeyCookie();
        HttpClient.credentials();
    },

    clear: function() {
        for (let i = 0; i < 8; ++i) {
            Register.textboxes[i].value = '';
        }
    }
}