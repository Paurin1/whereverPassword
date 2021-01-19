function Array2d(x, y) {
    let ret = new Array(x);
    for (let i = 0; i < x; ++i)
        ret[i] = new Array(y).fill(0);
    return ret;
}

function toHexString(byteArray) {
    return Array.from(byteArray, function(byte) {
      return ('0' + (byte & 0xFF).toString(16)).slice(-2);
    }).join('');
}

var Rij = {
    rij_created: false,

    create: function() {
        if (Rij.rij_created)
            return;

        Rij.num_rounds = {16: {16: 10, 24: 12, 32: 14}, 24: {16: 12, 24: 12, 32: 14}, 32: {16: 14, 24: 14, 32: 14}};
        Rij.shifts = [
            [[0, 0], [1, 3], [2, 2], [3, 1]],
            [[0, 0], [1, 5], [2, 4], [3, 3]],
            [[0, 0], [1, 7], [3, 5], [4, 4]]
        ];

        let A = [
            [1, 1, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 1, 1, 1],
            [1, 1, 1, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 0, 0, 0, 1]
        ];
        
        // produce log and alog tables, needed for multiplying in the
        // field GF(2^m) (generator = 3)
        let alog = [1];
        for (let i = 0; i < 255; ++i) {
            let j = (alog[alog.length - 1] << 1) ^ alog[alog.length - 1];
            if ((j & 0x100) != 0)
                j ^= 0x11B;
            alog.push(j);
        }

        let log = new Array(256).fill(0);

        for (let i = 1; i < 255; ++i) {
            log[alog[i]] = i;
        }

        // multiply two elements of GF(2^m)
        let mul = function(a, b) {
            if (a == 0 || b == 0)
                return 0;
            return alog[(log[a & 0xFF] + log[b & 0xFF]) % 255];
        }

        // substitution box based on F^{-1}(x)
        let box = Array2d(256, 8);
        box[1][7] = 1;

        for (let i = 2; i < 256; ++i) {
            let j = alog[255 - log[i]]
            for (let t = 0; t < 8; ++t) {
                box[i][t] = (j >> (7 - t)) & 0x01;
            }
        }

        let B = [0, 1, 1, 0, 0, 0, 1, 1];

        // affine transform:  box[i] <- B + A*box[i]
        let cox = Array2d(256, 8);
        for (let i = 0; i < 256; ++i) {
            for (let t = 0; t < 8; ++t) {
                cox[i][t] = B[t];
                for (let j = 0; j < 8; ++j) {
                    cox[i][t] ^= A[t][j] * box[i][j];
                }
            }
        }

        // cls.S-boxes and inverse cls.S-boxes
        Rij.S =  new Array(256).fill(0);
        Rij.Si = new Array(256).fill(0);
        for (let i = 0; i < 256; ++i) {
            Rij.S[i] = cox[i][0] << 7;
            for (let t = 1; t < 8; ++t) {
                Rij.S[i] ^= cox[i][t] << (7-t)
            }
            Rij.Si[Rij.S[i] & 0xFF] = i;
        }

        // T-boxes
        let G = [
            [2, 1, 1, 3],
            [3, 2, 1, 1],
            [1, 3, 2, 1],
            [1, 1, 3, 2]
        ];

        let AA = Array2d(4, 8);

        for (let i = 0; i < 4; ++i) {
            for (let j = 0; j < 4; ++j) {
                AA[i][j] = G[i][j];
                AA[i][i+4] = 1;
            }
        }

        for (let i = 0; i < 4; ++i) {
            let pivot = AA[i][i];
            if (pivot == 0) {
                t = i + 1;
                while(AA[t][i] == 0 && t < 4) {
                    t += 1;

                    if (t == 4)
                        throw 'G matrix must be invertible, t == ' + t;

                    for (let j = 0; j < 8; ++j) {
                        AA[i][j] = AA[t][j];
                        AA[t][j] = AA[i][j];
                    }

                    pivot = AA[i][i];
                }
            }

            for (let j = 0; j < 8; ++j) {
                if (AA[i][j] != 0)
                    AA[i][j] = alog[(255 + log[AA[i][j] & 0xFF] - log[pivot & 0xFF]) % 255];
            }

            for (let t = 0; t < 4; ++t) {
                if (i != t) {
                    for (let j = i+1; j < 8; ++j)
                        AA[t][j] ^= mul(AA[i][j], AA[t][i]);
                    AA[t][i] = 0;
                }
            }
        }

        let iG = Array2d(4, 4);

        for (let i = 0; i < 4; ++i){
            for (let j = 0; j < 4; ++j) {
                iG[i][j] = AA[i][j + 4];
            }
        }

        let mul4 = function(a, bs) {
            if (a == 0)
                return 0;

            let r = 0;
            for (let i = 0; i < bs.length; ++i) {
                r <<= 8;
                if (bs[i] != 0)
                    r = r | mul(a, bs[i]);
            }

            return (new Uint32Array([r]))[0];
        }
        
        Rij.T1 = new Array();
        Rij.T2 = new Array();
        Rij.T3 = new Array();
        Rij.T4 = new Array();
        Rij.T5 = new Array();
        Rij.T6 = new Array();
        Rij.T7 = new Array();
        Rij.T8 = new Array();
        Rij.U1 = new Array();
        Rij.U2 = new Array();
        Rij.U3 = new Array();
        Rij.U4 = new Array();

        for (let t = 0; t < 256; ++t) {
            let s = Rij.S[t];
            Rij.T1.push(mul4(s, G[0]))
            Rij.T2.push(mul4(s, G[1]))
            Rij.T3.push(mul4(s, G[2]))
            Rij.T4.push(mul4(s, G[3]))

            s = Rij.Si[t]
            Rij.T5.push(mul4(s, iG[0]))
            Rij.T6.push(mul4(s, iG[1]))
            Rij.T7.push(mul4(s, iG[2]))
            Rij.T8.push(mul4(s, iG[3]))

            Rij.U1.push(mul4(t, iG[0]))
            Rij.U2.push(mul4(t, iG[1]))
            Rij.U3.push(mul4(t, iG[2]))
            Rij.U4.push(mul4(t, iG[3]))
        }
        
        // round constants
        Rij.rcon = [1];
        let r = 1;
        for (let t = 1; t < 30; ++t) {
            r = mul(2, r);
            Rij.rcon.push(r);
        }

        Rij.rij_created = true;
    },

    getKeyBytes: function(key) {
        let keynums = [];
        
        for (let i = 0; i < key.length; ++i) {
            keynums.push( key.charCodeAt(i) );
        }

        return keynums;
    },

    // key: ArrayBuffer
    init: function(key) {
        // create common meta-instance infrastructure
        Rij.create();

        Rij.block_size = key.length;

        if (Rij.block_size != 16 && Rij.block_size != 24 && Rij.block_size != 32)
            throw 'Invalid key size';

        let ROUNDS = Rij.num_rounds[key.length][Rij.block_size];
        let BC = Math.floor(Rij.block_size / 4);

        // encryption round keys
        let Ke = Array2d(ROUNDS + 1, BC); // new Array(ROUNDS + 1).fill(new Array(BC).fill(0));

        // decryption round keys
        let Kd = Array2d(ROUNDS + 1, BC); // new Array(ROUNDS + 1).fill(new Array(BC).fill(0));

        Rij.round_key_count = (ROUNDS + 1) * BC;
        Rij.kc = Math.floor(key.length / 4);

        key = Rij.getKeyBytes(key);

        // copy user material bytes into temporary ints
        let tk = new Array();
        for (let i = 0; i < Rij.kc; ++i) {
            tk.push(
                (key[i * 4]     << 24) | 
                (key[i * 4 + 1] << 16) |
                (key[i * 4 + 2] << 8) | 
                 key[i * 4 + 3]
            );
        }

        // copy values into round key arrays
        let t = 0, j = 0;
        while (j < Rij.kc && t < Rij.round_key_count) {
            Ke[Math.floor(t / BC)][t % BC] = tk[j];
            Kd[ROUNDS - (Math.floor(t / BC))][t % BC] = tk[j];
            j += 1;
            t += 1;
        }

        let tt = 0;
        let rconpointer = 0;

        while (t < Rij.round_key_count) {
            // extrapolate using phi (the round key evolution function)
            tt = tk[Rij.kc - 1];
            tk[0] ^= (Rij.S[(tt >> 16) & 0xFF] & 0xFF) << 24 ^
                     (Rij.S[(tt >>  8) & 0xFF] & 0xFF) << 16 ^
                     (Rij.S[ tt        & 0xFF] & 0xFF) <<  8 ^
                     (Rij.S[(tt >> 24) & 0xFF] & 0xFF)       ^
                     (Rij.rcon[rconpointer]    & 0xFF) << 24;
            rconpointer += 1;

            if (Rij.kc != 8) {
                for (let i = 1; i < Rij.kc; ++i) {
                    tk[i] ^= tk[i-1];
                }
            }
            else {
                for (let i = 1; i < Math.floor(Rij.kc / 2); ++i) {
                    tk[i] ^= tk[i-1];
                }
                tt = tk[Math.floor(Rij.kc / 2 - 1)];
            }

            tk[Math.floor(Rij.kc / 2)] ^=
                (Rij.S[ tt        & 0xFF] & 0xFF)       ^
                (Rij.S[(tt >>  8) & 0xFF] & 0xFF) <<  8 ^
                (Rij.S[(tt >> 16) & 0xFF] & 0xFF) << 16 ^
                (Rij.S[(tt >> 24) & 0xFF] & 0xFF) << 24;

            for (let i = Math.floor(Rij.kc / 2) + 1; i < Rij.kc; ++i) {
                tk[i] ^= tk[i-1];
            }

            // copy values into round key arrays
            let j = 0;
            while (j < Rij.kc && t < Rij.round_key_count) {
                Ke[Math.floor(t / BC)][t % BC] = (new Uint32Array([tk[j]]))[0];
                Kd[ROUNDS - (Math.floor(t / BC))][t % BC] = tk[j];
                j += 1;
                t += 1;
            }
        }
        
        // inverse MixColumn where needed
        for (let r = 1; r < ROUNDS; ++r) {
            for (let j = 0; j < BC; ++j) {
                let tt = Kd[r][j];
                Kd[r][j] = (new Uint32Array([
                    Rij.U1[(tt >> 24) & 0xFF] ^
                    Rij.U2[(tt >> 16) & 0xFF] ^
                    Rij.U3[(tt >>  8) & 0xFF] ^
                    Rij.U4[ tt        & 0xFF]
                ]))[0];
            }
        }

        Rij.Ke = Ke;
        Rij.Kd = Kd;
    },

    // textbytes: ArrayBuffer
    _encrypt: function(textbytes) {
        if (textbytes.length != Rij.block_size)
            throw 'block length does not match key size';

        textbytes = Rij.getKeyBytes(textbytes);

        let Ke = Rij.Ke;

        let BC = Math.floor(Rij.block_size / 4);
        let ROUNDS = Ke.length - 1;

        if (BC == 4)
            Rij.sc = 0;

        else if (BC == 6)
            Rij.sc = 1;

        else
            Rij.sc = 2;

        let s1 = Rij.shifts[Rij.sc][1][0];
        let s2 = Rij.shifts[Rij.sc][2][0];
        let s3 = Rij.shifts[Rij.sc][3][0];
        let a = new Array(BC).fill(0);

        // temporary work array
        let t = new Array();

        // plaintext to ints + key
        for (let i = 0; i < BC; ++i) {
            t.push(
               (textbytes[i * 4    ] << 24 |
                textbytes[i * 4 + 1] << 16 |
                textbytes[i * 4 + 2] <<  8 |
                textbytes[i * 4 + 3]        ) ^ Ke[0][i]
            );
        }

        // apply round transforms
        for (let r = 1; r < ROUNDS; ++r) {
            for (let i = 0; i < BC; ++i) {
                a[i] = (Rij.T1[(t[ i               ] >> 24) & 0xFF] ^
                        Rij.T2[(t[(i + s1) % BC] >> 16) & 0xFF] ^
                        Rij.T3[(t[(i + s2) % BC] >>  8) & 0xFF] ^
                        Rij.T4[ t[(i + s3) % BC]        & 0xFF]  ) ^ Ke[r][i];
            }

            t = new Array(a.length);
            for (let i = 0; i < a.length; ++i) {
                t[i] = a[i];
            }
        }

        // last round is special
        let result = new Array();

        for (let i = 0; i < BC; ++i) {
            let tt = Ke[ROUNDS][i];
            result.push((Rij.S[(t[ i               ] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF);
            result.push((Rij.S[(t[(i + s1) % BC] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF);
            result.push((Rij.S[(t[(i + s2) % BC] >>  8) & 0xFF] ^ (tt >>  8)) & 0xFF);
            result.push((Rij.S[ t[(i + s3) % BC]        & 0xFF] ^  tt       ) & 0xFF);
        }

        return result;
    },

    // cipherbytes: ArrayBuffer
    _decrypt: function(cipherbytes) {
        if (cipherbytes.length != Rij.block_size)
            throw 'block length does not match key size';

        let Kd = Rij.Kd;

        let BC = Math.floor(Rij.block_size / 4);
        let ROUNDS = Kd.length - 1;

        if (BC == 4)
            Rij.sc = 0;

        else if (BC == 6)
            Rij.sc = 1;

        else
            Rij.sc = 2;

        let s1 = Rij.shifts[Rij.sc][1][1];
        let s2 = Rij.shifts[Rij.sc][2][1];
        let s3 = Rij.shifts[Rij.sc][3][1];
        let a = new Array(BC).fill(0);
        
        // temporary work array
        let t = new Array(BC).fill(0);

        // cipherbytes to ints + key
        for (let i = 0; i < BC; ++i) {
            t[i] = (cipherbytes[i * 4    ] << 24 |
                    cipherbytes[i * 4 + 1] << 16 |
                    cipherbytes[i * 4 + 2] <<  8 |
                    cipherbytes[i * 4 + 3]        ) ^ Kd[0][i];
        }

        // apply round transforms
        for (let r = 1; r < ROUNDS; ++r) {
            for (let i = 0; i < BC; ++i) {
                a[i] = (Rij.T5[(t[ i               ] >> 24) & 0xFF] ^
                        Rij.T6[(t[(i + s1) % BC] >> 16) & 0xFF] ^
                        Rij.T7[(t[(i + s2) % BC] >>  8) & 0xFF] ^
                        Rij.T8[ t[(i + s3) % BC]        & 0xFF]  ) ^ Kd[r][i];
            }

            t = new Array(a.length);
            for (let i = 0; i < a.length; ++i) {
                t[i] = a[i];
            }
        }

        // last round is special
        let result = new Array();

        for (let i = 0; i < BC; ++i) {
            tt = Kd[ROUNDS][i];
            result.push((Rij.Si[(t[ i               ] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF);
            result.push((Rij.Si[(t[(i + s1) % BC] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF);
            result.push((Rij.Si[(t[(i + s2) % BC] >>  8) & 0xFF] ^ (tt >>  8)) & 0xFF);
            result.push((Rij.Si[ t[(i + s3) % BC]        & 0xFF] ^  tt       ) & 0xFF);
        }

        return result;
    },

    // asciitext: String
    encrypt: function(asciitext) {
        let text_length = asciitext.length;
        let num_of_blocks = Math.ceil(text_length / Rij.block_size);
        let padding_len = Rij.block_size - (text_length - Rij.block_size * (num_of_blocks - 1));

        for (let i = 0; i < padding_len; ++i) {
            asciitext += '\0';
        }

        let encrypted = new Array();

        for (let block_num = 0; block_num < num_of_blocks; ++block_num) {
            encrypted = [...encrypted, ...Rij._encrypt(asciitext.substring(block_num * Rij.block_size, (block_num + 1) * Rij.block_size))];
        }

        return toHexString(encrypted);
    },

    hexToUnsignedInt: function (inputStr) {
        var hex  = inputStr.toString();
        var Uint8Array = new Array();
        for (var n = 0; n < hex.length; n += 2) {
          Uint8Array.push(parseInt(hex.substr(n, 2), 16));
        }
        return Uint8Array;
    },

    // ciphertext: String
    decrypt: function(ciphertext) {
        ciphertext = Rij.hexToUnsignedInt(ciphertext);

        let num_of_blocks = Math.floor(ciphertext.length / Rij.block_size);

        let decrypted = new Array();

        for (let block_num = 0; block_num < num_of_blocks; ++block_num) {
            decrypted = [...decrypted, ...Rij._decrypt(ciphertext.slice(block_num * Rij.block_size, (block_num + 1) * Rij.block_size))];
        }

        let dec_str = '';

        for (let i = 0; i < decrypted.length; ++i) {
            if (decrypted[i] == 0)
                break;

            dec_str += String.fromCharCode(decrypted[i]);
        }

        return dec_str;
    }
}
