import json
import pyaes

# if name == None -> list of entries
#    name != None -> details on entry[name]
def read(fn, key, name=None):
    # load AES key
    aes = pyaes.Rijndael(key)

    # read the passwords file
    with open('users/{}.ejson'.format(fn), 'rb') as fs:
        # decrypt file's content
        file_text = aes.decrypt(fs.read())

        # validate if decrypted data is a JSON string
        try:
            passwords = json.loads(file_text)
        except:
            raise Exception("Invalid master key")

        if name:
            return passwords[name]

        else:
            ret_list = []

            for entry in passwords.values():
                ret_list.append({
                    'name': entry['name'],
                    'url': entry['url']
                })

            return ret_list