from copy import deepcopy
from math import ceil
from binascii import hexlify

class Rijndael(object):
    @classmethod
    def create(cls):

        if hasattr(cls, "RIJNDAEL_CREATED"):
            return

        # [keysize][block_size]
        cls.num_rounds = {16: {16: 10, 24: 12, 32: 14}, 24: {16: 12, 24: 12, 32: 14}, 32: {16: 14, 24: 14, 32: 14}}

        cls.shifts = [[[0, 0], [1, 3], [2, 2], [3, 1]],
                [[0, 0], [1, 5], [2, 4], [3, 3]],
                [[0, 0], [1, 7], [3, 5], [4, 4]]]

        A = [[1, 1, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 1, 1, 1],
            [1, 1, 1, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 0, 0, 0, 1]]

        # produce log and alog tables, needed for multiplying in the
        # field GF(2^m) (generator = 3)
        alog = [1]
        for i in range(255):
            j = (alog[-1] << 1) ^ alog[-1]
            if j & 0x100 != 0:
                j ^= 0x11B
            alog.append(j)

        log = [0] * 256
        for i in range(1, 255):
            log[alog[i]] = i

        # multiply two elements of GF(2^m)
        def mul(a, b):
            if a == 0 or b == 0:
                return 0
            return alog[(log[a & 0xFF] + log[b & 0xFF]) % 255]

        # substitution box based on F^{-1}(x)
        box = [[0] * 8 for i in range(256)]
        box[1][7] = 1
        for i in range(2, 256):
            j = alog[255 - log[i]]
            for t in range(8):
                box[i][t] = (j >> (7 - t)) & 0x01

        B = [0, 1, 1, 0, 0, 0, 1, 1]

        # affine transform:  box[i] <- B + A*box[i]
        cox = [[0] * 8 for i in range(256)]
        for i in range(256):
            for t in range(8):
                cox[i][t] = B[t]
                for j in range(8):
                    cox[i][t] ^= A[t][j] * box[i][j]

        # cls.S-boxes and inverse cls.S-boxes
        cls.S =  [0] * 256
        cls.Si = [0] * 256
        for i in range(256):
            cls.S[i] = cox[i][0] << 7
            for t in range(1, 8):
                cls.S[i] ^= cox[i][t] << (7-t)
            cls.Si[cls.S[i] & 0xFF] = i

        # T-boxes
        G = [[2, 1, 1, 3],
            [3, 2, 1, 1],
            [1, 3, 2, 1],
            [1, 1, 3, 2]]

        AA = [[0] * 8 for i in range(4)]

        for i in range(4):
            for j in range(4):
                AA[i][j] = G[i][j]
                AA[i][i+4] = 1

        for i in range(4):
            pivot = AA[i][i]
            if pivot == 0:
                t = i + 1
                while AA[t][i] == 0 and t < 4:
                    t += 1
                    assert t != 4, 'G matrix must be invertible'
                    for j in range(8):
                        AA[i][j], AA[t][j] = AA[t][j], AA[i][j]
                    pivot = AA[i][i]
            for j in range(8):
                if AA[i][j] != 0:
                    AA[i][j] = alog[(255 + log[AA[i][j] & 0xFF] - log[pivot & 0xFF]) % 255]
            for t in range(4):
                if i != t:
                    for j in range(i+1, 8):
                        AA[t][j] ^= mul(AA[i][j], AA[t][i])
                    AA[t][i] = 0

        iG = [[0] * 4 for i in range(4)]

        for i in range(4):
            for j in range(4):
                iG[i][j] = AA[i][j + 4]

        def mul4(a, bs):
            if a == 0:
                return 0
            r = 0
            for b in bs:
                r <<= 8
                if b != 0:
                    r = r | mul(a, b)
            return r

        cls.T1 = []
        cls.T2 = []
        cls.T3 = []
        cls.T4 = []
        cls.T5 = []
        cls.T6 = []
        cls.T7 = []
        cls.T8 = []
        cls.U1 = []
        cls.U2 = []
        cls.U3 = []
        cls.U4 = []

        for t in range(256):
            s = cls.S[t]
            cls.T1.append(mul4(s, G[0]))
            cls.T2.append(mul4(s, G[1]))
            cls.T3.append(mul4(s, G[2]))
            cls.T4.append(mul4(s, G[3]))

            s = cls.Si[t]
            cls.T5.append(mul4(s, iG[0]))
            cls.T6.append(mul4(s, iG[1]))
            cls.T7.append(mul4(s, iG[2]))
            cls.T8.append(mul4(s, iG[3]))

            cls.U1.append(mul4(t, iG[0]))
            cls.U2.append(mul4(t, iG[1]))
            cls.U3.append(mul4(t, iG[2]))
            cls.U4.append(mul4(t, iG[3]))

        # round constants
        cls.rcon = [1]
        r = 1
        for t in range(1, 30):
            r = mul(2, r)
            cls.rcon.append(r)

        cls.RIJNDAEL_CREATED = True

    # key: array of numbers, eg. int list, bytes
    def __init__(self, key):

        # create common meta-instance infrastructure
        self.create()

        block_size = len(key)

        if block_size != 16 and block_size != 24 and block_size != 32:
            raise ValueError('Invalid block size: ' + str(block_size))
        if len(key) != 16 and len(key) != 24 and len(key) != 32:
            raise ValueError('Invalid key size: ' + str(len(key)))
        self.block_size = block_size

        ROUNDS = Rijndael.num_rounds[len(key)][block_size]
        BC = int(block_size / 4)
        # encryption round keys
        Ke = [[0] * BC for i in range(ROUNDS + 1)]
        # decryption round keys
        Kd = [[0] * BC for i in range(ROUNDS + 1)]
        ROUND_KEY_COUNT = (ROUNDS + 1) * BC
        KC = int(len(key) / 4)

        # copy user material bytes into temporary ints
        tk = []
        for i in range(0, KC):
            tk.append((key[i * 4] << 24) | (key[i * 4 + 1] << 16) |
                (key[i * 4 + 2] << 8) | key[i * 4 + 3])

        # copy values into round key arrays
        t = 0
        j = 0
        while j < KC and t < ROUND_KEY_COUNT:
            Ke[int(t / BC)][t % BC] = tk[j]
            Kd[ROUNDS - (int(t / BC))][t % BC] = tk[j]
            j += 1
            t += 1
        tt = 0
        rconpointer = 0
        while t < ROUND_KEY_COUNT:
            # extrapolate using phi (the round key evolution function)
            tt = tk[KC - 1]
            tk[0] ^= (Rijndael.S[(tt >> 16) & 0xFF] & 0xFF) << 24 ^  \
                     (Rijndael.S[(tt >>  8) & 0xFF] & 0xFF) << 16 ^  \
                     (Rijndael.S[ tt        & 0xFF] & 0xFF) <<  8 ^  \
                     (Rijndael.S[(tt >> 24) & 0xFF] & 0xFF)       ^  \
                     (Rijndael.rcon[rconpointer]    & 0xFF) << 24
            rconpointer += 1
            if KC != 8:
                for i in range(1, KC):
                    tk[i] ^= tk[i-1]
            else:
                for i in range(1, int(KC / 2)):
                    tk[i] ^= tk[i-1]
                tt = tk[int(KC / 2 - 1)]
                tk[int(KC / 2)] ^= (Rijndael.S[ tt        & 0xFF] & 0xFF)       ^ \
                              (Rijndael.S[(tt >>  8) & 0xFF] & 0xFF) <<  8 ^ \
                              (Rijndael.S[(tt >> 16) & 0xFF] & 0xFF) << 16 ^ \
                              (Rijndael.S[(tt >> 24) & 0xFF] & 0xFF) << 24
                for i in range(int(KC / 2) + 1, KC):
                    tk[i] ^= tk[i-1]
            # copy values into round key arrays
            j = 0
            while j < KC and t < ROUND_KEY_COUNT:
                Ke[int(t / BC)][t % BC] = tk[j]
                Kd[ROUNDS - (int(t / BC))][t % BC] = tk[j]
                j += 1
                t += 1
        # inverse MixColumn where needed
        for r in range(1, ROUNDS):
            for j in range(BC):
                tt = Kd[r][j]
                Kd[r][j] = Rijndael.U1[(tt >> 24) & 0xFF] ^ \
                           Rijndael.U2[(tt >> 16) & 0xFF] ^ \
                           Rijndael.U3[(tt >>  8) & 0xFF] ^ \
                           Rijndael.U4[ tt        & 0xFF]
        self.Ke = Ke
        self.Kd = Kd

    # textbytes: array of numbers, eg. int list, bytes
    def _encrypt(self, textbytes):
        if len(textbytes) != self.block_size:
            raise ValueError('wrong block length, expected ' + str(self.block_size) + ' got ' + str(len(textbytes)))
        Ke = self.Ke

        BC = int(self.block_size / 4)
        ROUNDS = len(Ke) - 1
        if BC == 4:
            Rijndael.SC = 0
        elif BC == 6:
            Rijndael.SC = 1
        else:
            Rijndael.SC = 2
        s1 = Rijndael.shifts[Rijndael.SC][1][0]
        s2 = Rijndael.shifts[Rijndael.SC][2][0]
        s3 = Rijndael.shifts[Rijndael.SC][3][0]
        a = [0] * BC

        # temporary work array
        t = []

        # plaintext to ints + key
        for i in range(BC):
            t.append((textbytes[i * 4    ] << 24 |
                      textbytes[i * 4 + 1] << 16 |
                      textbytes[i * 4 + 2] <<  8 |
                      textbytes[i * 4 + 3]        ) ^ Ke[0][i])

        # apply round transforms
        for r in range(1, ROUNDS):
            for i in range(BC):
                a[i] = (Rijndael.T1[(t[ i           ] >> 24) & 0xFF] ^
                        Rijndael.T2[(t[(i + s1) % BC] >> 16) & 0xFF] ^
                        Rijndael.T3[(t[(i + s2) % BC] >>  8) & 0xFF] ^
                        Rijndael.T4[ t[(i + s3) % BC]        & 0xFF]  ) ^ Ke[r][i]
            t = deepcopy(a)

        # last round is special
        result = []
        for i in range(BC):
            tt = Ke[ROUNDS][i]
            result.append((Rijndael.S[(t[ i           ] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF)
            result.append((Rijndael.S[(t[(i + s1) % BC] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF)
            result.append((Rijndael.S[(t[(i + s2) % BC] >>  8) & 0xFF] ^ (tt >>  8)) & 0xFF)
            result.append((Rijndael.S[ t[(i + s3) % BC]        & 0xFF] ^  tt       ) & 0xFF)

        return bytes(result)

    # cipherbytes: array of numbers, eg. int list, bytes
    def _decrypt(self, cipherbytes):
        if len(cipherbytes) != self.block_size:
            raise ValueError('wrong block length, expected ' + str(self.block_size) + ' got ' + str(len(cipherbytes)))
        Kd = self.Kd

        BC = int(self.block_size / 4)
        ROUNDS = len(Kd) - 1
        if BC == 4:
            Rijndael.SC = 0
        elif BC == 6:
            Rijndael.SC = 1
        else:
            Rijndael.SC = 2
        s1 = Rijndael.shifts[Rijndael.SC][1][1]
        s2 = Rijndael.shifts[Rijndael.SC][2][1]
        s3 = Rijndael.shifts[Rijndael.SC][3][1]
        a = [0] * BC

        # temporary work array
        t = [0] * BC

        # ciphertext to ints + key
        for i in range(BC):
            t[i] = (cipherbytes[i * 4    ] << 24 |
                    cipherbytes[i * 4 + 1] << 16 |
                    cipherbytes[i * 4 + 2] <<  8 |
                    cipherbytes[i * 4 + 3]        ) ^ Kd[0][i]

        # apply round transforms
        for r in range(1, ROUNDS):
            for i in range(BC):
                a[i] = (Rijndael.T5[(t[ i           ] >> 24) & 0xFF] ^
                        Rijndael.T6[(t[(i + s1) % BC] >> 16) & 0xFF] ^
                        Rijndael.T7[(t[(i + s2) % BC] >>  8) & 0xFF] ^
                        Rijndael.T8[ t[(i + s3) % BC]        & 0xFF]  ) ^ Kd[r][i]
            t = deepcopy(a)
            
        # last round is special
        result = []
        for i in range(BC):
            tt = Kd[ROUNDS][i]
            result.append((Rijndael.Si[(t[ i           ] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF)
            result.append((Rijndael.Si[(t[(i + s1) % BC] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF)
            result.append((Rijndael.Si[(t[(i + s2) % BC] >>  8) & 0xFF] ^ (tt >>  8)) & 0xFF)
            result.append((Rijndael.Si[ t[(i + s3) % BC]        & 0xFF] ^  tt       ) & 0xFF)
        return bytes(result)

    # asciitext: ascii str / bytes
    def encrypt(self, asciitext, hex=False):
        # str -> bytes
        if type(asciitext) == str:
            asciitext = bytes(asciitext, 'ascii')

        text_length = len(asciitext)
        num_of_blocks = int(ceil(text_length / self.block_size))
        padding_len = self.block_size - (text_length - self.block_size * (num_of_blocks - 1))

        asciitext += bytes([0]*padding_len)
        encrypted = b''

        for block_num in range(num_of_blocks):
            encrypted += self._encrypt(asciitext[block_num * self.block_size : (block_num + 1) * self.block_size])

        if hex:
            return hexlify(encrypted).decode('ascii')
        else:
            return encrypted

    # ciphertext: hex str
    def decrypt(self, ciphertext, hex=False):
        if hex:
            # hex -> bytes
            ciphertext = bytearray.fromhex(ciphertext)

        num_of_blocks = int(len(ciphertext) / self.block_size)
        decrypted = b''

        for block_num in range(num_of_blocks):
            decrypted += self._decrypt(ciphertext[block_num * self.block_size : (block_num + 1) * self.block_size])

        return decrypted.decode('ascii').strip('\0')