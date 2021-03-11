import base64
from pykeepass import PyKeePass

'''
    This function is not yet implemented properly.
'''
def read(username, password, name=None):
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