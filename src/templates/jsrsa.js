const pk_n = '{{ rsa_key_n }}';
const pk_e = '{{ rsa_key_e }}';

// key - hex string representing key bytes
function encryptRSA(key) {
    // create bigInt objects
    let n = bigInt(pk_n, 16);
    let e = bigInt(pk_e, 16);
    let m = bigInt(key, 16);

    // perform encryption and return result as string representing hex value of this number
    // m^e mod n
    return m.modPow(e, n).toString(16);
}