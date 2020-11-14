from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict
import simplejson as json
from skelbimai import database, methods
from django.db import connection
from django.conf import settings
from datetime import datetime

#users/
#GET - gauti vartotojų sąrašą
#POST - sukurti vartotoją
@csrf_exempt
def userAPI1(request):  
    if (request.method == 'GET'):
        resultDetails = getUserList(request)
    elif (request.method == 'POST'):
        resultDetails = createUser(request)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])
    
#users/<int:index>/
#PUT - atnaujinti vartotojo informaciją (pvz: telefoną, e.paštą)
#DELETE - panaikinti vartotoją
#GET - gauti vieno vartotojo informaciją
@csrf_exempt
def userAPI2(request, index):  
    if (request.method == 'PUT'):
        resultDetails = updateUser(request, index)
    elif (request.method == 'DELETE'):
        resultDetails = deleteUser(request, index)
    elif (request.method == 'GET'):
        resultDetails = getUser(request, index)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])

@csrf_exempt
def userAPI3(request):  
    if (request.method == 'POST'):
        resultDetails = getClientId(request)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])

    
def getUserList(request):
    statusCode = 200 #403
    result = Path('skelbimai/jsonmock/userList.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
    return [result, content_type, statusCode]

def createUser(request):
    result = ""
    content_type = None
    statusCode = 201
    bodyData = QueryDict(request.body)
    for x in bodyData:
        body = x
    body = methods.loadJson(body)
    if body == None or not isinstance(body,dict):
        return [result, content_type, 400]
    if not checkCreateUser(body):
        return [result, content_type, 400]
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM public.user WHERE username = %s", [body["username"]])
        row = database.dictfetchall(cursor)
        if row[0]["count"] != 0:
            statusCode = 409
        else:
            cursor.execute("INSERT INTO public.user (username, name, phone, email, usersince_date, role, is_deleted, client_id, password) VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s);",
                [body["username"], body["name"], body["phone"], body["email"], methods.currentTime(), "user", methods.generate_client_id(), methods.hash_password(body["password"])])
    return [result, content_type, statusCode]

def getClientId(request):
    result = ""
    content_type = None
    statusCode = 200 #401
    username = ""
    password = ""
    bodyData = QueryDict(request.body)
    for x in bodyData:
        body = x
    body = methods.loadJson(body)
    if body == None or not isinstance(body,dict):
        return [result, content_type, 400]
    if "username" in body and "password" in body:
        username = body["username"]
        password = body["password"]
    else:
        return [result, content_type, 400]
    with connection.cursor() as cursor:
        cursor.execute("SELECT password, client_id FROM public.user WHERE username = %s", [username])
        row = database.dictfetchall(cursor)
        if len(row) == 1:
            if not methods.verify_password(row[0]["password"], password):
                return [result, content_type, 401]
            else:
                content_type = "application/json"
                result = json.dumps({"client_id": row[0]["client_id"]})
        else:
            return [result, content_type, 401]
        
    return [result, content_type, statusCode]

def updateUser(request, index):
    statusCode = 200 #401 403 404
    result = ""
    content_type = None
    return [result, content_type, statusCode]
    
def deleteUser(request, index):
    statusCode = 200 #401 403 404
    result = ""
    content_type = None
    return [result, content_type, statusCode]
    
def getUser(request, index):
    statusCode = 200 #401 403 404
    result = Path('skelbimai/jsonmock/user.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
    return [result, content_type, statusCode]

#Jei True - viskas gerai
def checkCreateUser(body):
    required_collumns = ["name", "username", "password", "phone", "email"]
    for collumn in required_collumns:
        if collumn not in body:
            return False
    if len(body["name"]) > 20 or len(body["name"]) < 2:
        return False
    if len(body["username"]) > 20 or len(body["username"]) < 6:
        return False
    if len(body["password"]) > 50 or len(body["username"]) < 6:
        return False
    if len(body["phone"]) > 20 or len(body["phone"]) < 6:
        return False
    if len(body["email"]) > 50 or len(body["phone"]) < 6:
        return False
    for collumn in required_collumns:
        if isinstance(body[collumn], str):
            if body[collumn].find(' ') != -1:
                return False
    return True
    

        
