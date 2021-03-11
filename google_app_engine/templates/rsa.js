RSA = {
    pk_n: '{{ rsa_key_n }}',
    pk_e: '{{ rsa_key_e }}',

    // hex_string - hex string representing key bytes
    encrypt: function(hex_string) {
        // create bigInt objects
        let n = bigInt(RSA.pk_n, 16);
        let e = bigInt(RSA.pk_e, 16);
        let m = bigInt(hex_string, 16);
    
        // perform encryption and return result as string representing the hex value of this number
        // m^e mod n
        return m.modPow(e, n).toString(16);
    }
}