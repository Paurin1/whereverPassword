# WhereverPassword

**WP** is an Python/Flask app to 

## Table of contents
* [Features](#features)
* [Quick start](#quick-start)
  * [Home server](#home-server)
  * [Google App Engine](#google-app-engine)
* [Configuration](#configuration)
* [FAQ](#faq)
* [Future improvements](#future-improvements)
* [Contribution](#contribution)

## Features

## Quick start
### Self-hosted server
Make sure you have [Python 3](https://wiki.python.org/moin/BeginnersGuide/Download) and [git](https://git-scm.com/downloads) installed properly on your device.
```

> python --version
Python 3.8.3
> git --version
git version 2.27.0.windows.1
```
Navigate to a proper location and clone this repository.
```
> git clone https://github.com/Paurin1/whereverPassword.git
```
Install required dependencies.
```
cd whereverpassword
pip install -r requirements.txt
```
Start example application.
```
cd google*
python main.py
```
### Google App Engine
## Configuration
#### Converting KeePass to app-friendly *.ejson
*ejson* is just a JSON-formatted text file encrypted with AES. `src/kdbx2ejson.py` is a script that can help you convert your KeePass file to **.ejson*. You can try it in an example:
```
> cd examples/parser
> python kdbx2ejson.py example.kdbx somepassword12345 11110000111100001111000011110000
```
It should create file named `f5cb390d3c2e53aa1469252fff1b5e1c.ejson`. **WP** uses hashed AES keys to create files' names. It allows to quickly check if the key is valid without trying to decrypt every file available.

#### Parsing Firefox exported passwords
*Soon...*

## FAQ
### How are keys' hashes created?


## Future improvements
 - Add checkbox to prevent from saving cookies
 - Allow passwords updates
 - Improve frontend to be more appealing
 - Design frontend for mobile devices

## Contribution
* [pykeepass](https://github.com/libkeepass/pykeepass)
* [JavaScript Cookie](https://github.com/js-cookie/js-cookie)
* [BigInteger.js](https://github.com/peterolson/BigInteger.js/)
* [AES-JS](https://github.com/ricmoo/aes-js) (adjusted to fit **WP** needs)
* [Pure Python RSA](https://github.com/sybrenstuvel/python-rsa/) (adjusted to fit **WP** needs)
