MasterKey = {
    // number of days that cookie is stored on client's browser
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

    // returns lower case string of passwords key
    getKey: function() {
        let alnum = '';
        for (let i = 0; i < 8; ++i) {
            alnum += MasterKey.textboxes[i].value[0];
            alnum += MasterKey.textboxes[i].value[2];
            alnum += MasterKey.textboxes[i].value[4];
            alnum += MasterKey.textboxes[i].value[6];
        }
        return alnum.toLowerCase();
    },

    // checks if all textboxes are filled
    isReady: function() {
        for (let i = 0; i < 8; ++i) {
            if (MasterKey.textboxes[i].value.length != 7)
                return false;
    
            if (MasterKey.textboxes[i].value[1] != ' ' ||
                MasterKey.textboxes[i].value[3] != ' ' ||
                MasterKey.textboxes[i].value[5] != ' ')
                return false;
        }
        return true;
    },

    isAlnum: function(c) {
        if ((48 > c || c > 57) && (65 > c || c > 70) && (97 > c || c > 102))
            return false;
    
        return true;
    },

    // called each time value of a textbox changes (either by keyboard or paste)
    onChange: function() {
        // extract alnum
        let alnum = [];
        for (let i = 0; i < this.value.length; ++i) {
            if (MasterKey.isAlnum(this.value.charCodeAt(i)))
                alnum.push(this.value[i]);
    
            // limit to only 4 chars
            if (alnum.length == 4)
                break;
        }
    
        // add spaced in between
        this.value = alnum.join(' ');
        
        // check if it is worth validating key
        if (alnum.length == 4)
            if (MasterKey.isReady())
                MasterKey.apply();
    
            // change focus
            else {
                switch(this.id) {
                    case 'g1': MasterKey.textboxes[1].focus(); break;
                    case 'g2': MasterKey.textboxes[2].focus(); break;
                    case 'g3': MasterKey.textboxes[3].focus(); break;
                    case 'g4': MasterKey.textboxes[4].focus(); break;
                    case 'g5': MasterKey.textboxes[5].focus(); break;
                    case 'g6': MasterKey.textboxes[6].focus(); break;
                    case 'g7': MasterKey.textboxes[7].focus(); break;
                    case 'g8': MasterKey.textboxes[0].focus(); break;
                }
            }
    },

    // master key can be applied by ENTER
    onKeyUp: function(e) {
        if (e.keyCode === 13) {
            if (MasterKey.isReady())
                MasterKey.apply();
        }
    },

    // store encrypted master key in a cookie
    setKeyCookie: function() {
        let key = MasterKey.getKey();
        let enc_key = RSA.encrypt(key);

        Cookies.set('key', enc_key, { expires: MasterKey.cookie_expiration });
        Cookies.set('rsa', RSA.pk_n, { expires: MasterKey.cookie_expiration });
    },

    // send master key to the server to check if it is correct
    apply: function() {
        MasterKey.setKeyCookie();
        HttpClient.credentials();
    },

    clear: function() {
        for (let i = 0; i < 8; ++i) {
            MasterKey.textboxes[i].value = '';
        }
    }
}