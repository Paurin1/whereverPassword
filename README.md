# **WhereverPassword**

**WP** is a simple Python/Flask app for hosting passwords sharing server. You can see the demo [here](https://whereverpassword.oa.r.appspot.com/). </br>The master key is set to `1111-1111-1111-1111-1111-1111-1111-1111`.

## **Table of contents**
* [Quick start](#quick-start)
  * [Self-hosted server](#self-hosted-server)
  * [Google App Engine](#google-app-engine)
  * [How to use the website?](#how-to-use-the-website)
* [Configuration](#configuration)
* [FAQ](#faq)
  * [How does it work?](#how-does-it-work)
  * [How does it hash keys?](#how-does-it-hash-keys)
  * [Why MD5 and not bcrypt?](#why-md5-and-not-bcrypt)
  * [At what points does the user's master key is exposed?](#at-what-points-does-the-users-master-key-is-exposed)
  * [Why only 128 bits?](#why-only-128-bits)
  * [Is Raspberry Pi suitable for hosting?](#is-raspberry-pi-suitable-for-hosting)
  * [How can I upload my passwords to Google Cloud?](#how-can-i-upload-my-passwords-to-google-cloud)
  * [Is there a way for key entering to be more human-friendly?](#is-there-a-way-for-key-entering-to-be-more-human-friendly)
* [Future improvements](#future-improvements)
* [Third party](#third-party)

## **Quick start**
### **Self-hosted server**
Make sure you have [Python 3](https://wiki.python.org/moin/BeginnersGuide/Download) and [git](https://git-scm.com/downloads) installed properly on your device.
```
> python --version
Python 3.5.3
> git --version
git version 2.11.0
```
Navigate to a proper location and clone the repository.
```
> git clone https://github.com/Paurin1/whereverPassword.git
```
Install required dependencies.
```
> cd whereverPassword
> pip install -r requirements.txt
```
Configure and run your application.
```
> cd examples/selfhosted
> python server.py
```
Beware, that [this method is not safe](https://flask.palletsprojects.com/en/master/deploying/). App should be run through, e.g. [Gunicorn](https://docs.gunicorn.org/en/latest/install.html):
```
> gunicorn -b 0.0.0.0:80 server:app
```
### **Google App Engine**
You can host your **WP** server on Google App Engine. To do so visit [console.cloud.google.com](https://console.cloud.google.com/). 
  1. Create new project (beware that project's name will be a part of your server's url).
  2. On your left there is a button called `Activate Cloud Shell`.
  3. Set project for this session
```
username@cloudshell:~$ gcloud config set project your_project_name
Updated property [core/project].
```
  4. Clone Github repository
```
username@cloudshell:~ (your_project_name)$ git clone https://github.com/Paurin1/whereverPassword.git
Cloning into 'whereverPassword'...
[...], done.
```
  5. Navigate to the example directory
```
username@cloudshell:~ (your_project_name)$ cd whereverPassword/e*/g*
```
  6. Deploy the app:
```
username@cloudshell:~ (your_project_name)$ gcloud app deploy
```
### **How to use the website?**
  1. Type in the master key.
  2. Select desired entry.
  3. Click on username/password field to copy it to the clipboard.
     * keep in mind that the password will remain in the clipboard!
## **Configuration**
#### **Converting KeePass to \*.ejson**
*ejson* is just a JSON-formatted text file encrypted with AES. [`src/kdbx2ejson.py`](https://github.com/Paurin1/whereverPassword/blob/master/src/kdbx2ejson.py) is a script that can help you convert your KeePass file to **.ejson*. You can try it in an example:
```
> cd examples/parser
> python kdbx2ejson.py example.kdbx somepassword12345 11110000111100001111000011110000
```
It should create a file named `f5cb390d3c2e53aa1469252fff1b5e1c.ejson`. **WP** uses hashed AES keys to create files' names. It allows to quickly check if the key is valid without trying to decrypt every file available.

#### **Parsing passwords exported from Firefox**
Firefox exports passwords into `*.csv` file. Creating new or updating existing `*.ejson` file works in a similar way as in the previous example:
```
> cd examples/parser
> python ffcsv2ejson.py [...].csv 11110000111100001111000011110000
```

## **FAQ**
### **How does it work?**
#### **\*.ejson file**
 1. Your passwords are stored in a JSON-formatted string looking like this:
 ```json
 {
	 "[name]": {"name": "...", "url": "...", "username": "...", "password": "..."},
	 "[name]": {"name": "...", "url": "...", "username": "...", "password": "..."}
 }
 ```
 2. This string is encrypted with your 128-bit master key using AES encryption.
 3. Encrypted bytes are saved into `[hashed key].ejson` file where *hashed key* is a hashed master key.
 4. `*.ejson` file is placed into `users` directory. 

#### **Server side**
 1. Server always has its' RSA Public and Private keys loaded. RSA key size can be changed in [`pyrsa.py`](https://github.com/Paurin1/whereverPassword/blob/master/src/pyrsa.py).
 2. Public Key is sent to the client in [`rsa.js`](https://github.com/Paurin1/whereverPassword/blob/master/src/templates/rsa.js) file.
 3. During `/api` requests the server decrypts sent keys with its Private Key.
 4. When server responds to [`/api/list`](https://github.com/Paurin1/whereverPassword/blob/master/src/server.py#L42) or [`/api/details`](https://github.com/Paurin1/whereverPassword/blob/master/src/server.py#L82) it encrypts the response data with client's AES key.

#### **Client side**
1. Requests `http://servername:serverport/` and downloads every neccesary file.
(`rsa.js` file contains RSA Public Key that will be used to encrypt AES keys.)
2. In `main.js`:
	- generates 128-bit AES key that will be used to encrypt data from the server,
	- encrypts this key with server's Public Key,
	- checks whether `key` and `rsa` cookies are set,
	- checks if `rsa` cookie is the same as server's Public Key,
	- if any of above checks is `False` then acquire AES master key from the user.
3. After entering the master key, the key is validated by `/api/checkCredentials`.
4. If the key turns out to be correct, it is encrypted with server's Public Key and saved in a cookie file.
5. Each time client makes a request to [`/api/list`](https://github.com/Paurin1/whereverPassword/blob/master/src/static/network.js#L20) or [`/api/details`](https://github.com/Paurin1/whereverPassword/blob/master/src/static/network.js#L33) the encrypted master key is sent with the encrypted version of client's AES key.
### **How does it hash keys?**
```python
def hashKey(key):
    rounds_count = 128 * key[0] + key[1]
    for _ in range(rounds_count):
        key = md5(key).digest()
    return key.hex()
```
It uses key itself to determine how many rounds should it be encrypted with. In the worst case, it should not exceed *250ms* on *Raspberry Pi 3B*. This hash function can be adjusted to fit one's needs. If is a bit too fast for you then just modify the number of rounds, e.g.:
```python
rounds_count <<= 1
```
### **Why MD5 and not bcrypt?**
**bcrypt** hashes couldn't be used it their raw form as a file name.
**bcrypt** would not allow 0x00 bytes to be present in keys.
**MD5** seems to do a pretty decent work if you properly adjust the number of rounds. Susceptibility to collisions is irrelevent as you cannot decrypt ejson file with a MD5 collision.
Despite the above, **WP** will probably use **bcrypt** as soon as 192/256 bit keys are allowed.

### **Why only 128 bits?**
This seems to be a reasonable security measure that balances annoyance of entering an n-characters long key with a probability that someone will discover the server, hack into it, steal *.ejson file and try to decrypt it.

### **Is Raspberry Pi suitable for hosting?**
I was able to test it on *Raspberry Pi 3B* and a 2048-bit key worked with a response lag of 300ms. Some call it 'slow' but I prefer the term 'bruteforce-resistant'.

### **How can I upload my passwords to Google Cloud?**
To be honest, I don't know what is the best way to do so.
You can, e.g.:
  1. Upload it to your [Cloud Storage](https://cloud.google.com/storage/docs/uploading-objects).
  2. In uploaded file information you can find its' `Authenticated URL`.
  3. In Cloud Shell you can use the command `wget` to download the file
  ```
  username@cloudshell:~$ wget https://storage.cloud.google.com/your_project_name.appspot.com/key_hash.ejson
  ```

  ### **Is there a way for key entering to be more human-friendly?**
  I'm thinking about using some kind of pattern-unlock feature but I need to find a decent way of converting the pattern into a 128/192/256-bit key so that it does not lose it's strength.

## **Future improvements** 
(see [Issues](https://github.com/Paurin1/whereverPassword/issues))
 - Add checkbox to prevent from saving cookies
 - Allow passwords file updates
 - Improve frontend to be more appealing
 - Design different frontend for mobile devices
 - Allow 192/256-bit keys for AES
 - Experiment with different asymmetric encryptions, e.g. [ECC](https://en.wikipedia.org/wiki/Elliptic-curve_cryptography).


## **Third party**
* [pykeepass](https://github.com/libkeepass/pykeepass)
* [JavaScript Cookie](https://github.com/js-cookie/js-cookie)
* [BigInteger.js](https://github.com/peterolson/BigInteger.js/)
* [AES-JS](https://github.com/ricmoo/aes-js) (adjusted to fit **WP** needs)
* [Pure Python RSA](https://github.com/sybrenstuvel/python-rsa/) (adjusted to fit **WP** needs)
