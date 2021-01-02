import base64
import json
import pyaes

def read(username, password, name=None):
    """
        Takes username (filename), password, custom PIN or entry name as input and returns list of passwords or entry info.

        Arguments:
            username : str
                represents keepass file name: username.kdbx
            password : b64_str, 32 bytes long
                password bytes encoded in base64
            name : str, optional
                entry name

        Returns:
            name != None
                {
                    name : str,
                    username: str,
                    password: b64_str (utf-8 password),
                    url: str
                }

            name == None
                [
                    {
                        name : str, 
                        url : str
                    }, 
                    ...
                ]
    """
    # initialize decode
    aes = pyaes.Rijndael(base64.b64decode(bytes(password, 'ascii')))

    # read password file
    passes = None
    with open('{}.ejson'.format(username), 'rb') as fs:
        encrypted_file_bytes = fs.read()
        file_text = aes.decrypt(encrypted_file_bytes)
        try:
            passes = json.loads(file_text)
        except:
            raise Exception("Incorrect password")

    if name:
        for entry in passes:
            if entry['name'] == name:
                return {
                    'name': name,
                    'username': entry['username'],
                    'password': entry['password'],
                    'url': entry['url']
                }

    else:
        ret_list = []

        for entry in passes:
            ret_list.append({
                'name': entry['name'],
                'url': entry['url']
            })

        return ret_list