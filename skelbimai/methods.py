import simplejson as json
import hashlib, binascii, os
from random import choice
from string import ascii_uppercase
from django.conf import settings
from datetime import datetime, timedelta
from django.http import QueryDict
import jwt
def loadJson(jsonData):
    try:
        toReturn = json.loads(jsonData)
    except ValueError as err:
        return None
    return toReturn

def dumpJson(data):
    return json.dumps(data, ensure_ascii=False).encode('utf8')
    
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

def getRedirect_uri():
    return "https://skelbimai.azurewebsites.net/"

def get_admin_scopes():
    return ["ads", "categories", "comments", "user_admin"]

def get_user_scopes():
    return ["ads", "categories", "comments"]

def decode_token(auth):
    success = True
    result = ""
    token = auth.split()
    if len(token) == 2:
        if token[0] == "Bearer":
            try:
                result = jwt.decode(token[1], settings.SECRET, algorithms='HS256')
            except jwt.exceptions.DecodeError:
                success = False
                result = "wrong_input"
            except jwt.ExpiredSignatureError:
                success = False
                result = "expired"
    else:
        success = False
        result = "wrong_input"
    return [success, result]

def datetime_str(date):
    return date.strftime("%m/%d/%Y %H:%M:%S")

def get_body(bodyData):
    bodyData = QueryDict(bodyData)
    if len(bodyData) == 0:
        return [False, "empty"]
    for x in bodyData:
        body = x
    body = loadJson(body)
    if body == None or not isinstance(body,dict):
        return [False, body]
    else:
        return [True, body]