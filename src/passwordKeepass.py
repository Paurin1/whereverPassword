import base64
from pykeepass import PyKeePass

def read(username, password, name=None):
    """
        Takes username (filename), password, custom PIN or entry name as input and returns list of passwords or entry info.

        Arguments:
            username : str
                represents keepass file name: username.kdbx
            password : b64_str
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
    # decode password bytes
    password = base64.b64decode(bytes(password, 'ascii'))

    # modified pykeepass.kdbx_parsing.common line 110 -> so it can work on bytes
    kp = PyKeePass('{}.kdbx'.format(username), password=password)

    if name:
        for entry in kp.root_group.entries:
            if entry.title == name:
                return {
                    'name': entry.title,
                    'username': entry.username,
                    'password': base64.b64encode(entry.password.encode('utf-8')).decode('ascii'),
                    'url': entry.url
                }

    else:
        ret_list = []

        for entry in kp.root_group.entries:
            ret_list.append({
                'name': entry.title,
                'url': entry.url
            })

        return ret_list