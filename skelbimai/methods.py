import simplejson as json
from datetime import datetime
import hashlib, binascii, os
from random import choice
from string import ascii_uppercase
def loadJson(jsonData):
    try:
        toReturn = json.loads(jsonData)
    except ValueError as err:
        return None
    return toReturn

def currentTime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

 
def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')
 
def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def generate_client_id():
    return ''.join(choice(ascii_uppercase) for i in range(20))

