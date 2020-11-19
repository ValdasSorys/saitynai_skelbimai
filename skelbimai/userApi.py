from django.shortcuts import render
from django.db import connection, transaction, IntegrityError
from django.conf import settings
import jwt
import simplejson as json
from skelbimai import database, methods
from django.http import HttpResponse
from django.core import serializers
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

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

@csrf_exempt
def userAPI4(request):  
    if (request.method == 'POST'):
        resultDetails = getToken(request)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])
    
def getUserList(request):
    statusCode = 200 #403
    result = ""
    content_type = None
    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 401]
    scope = auth[1]["scope"]

    body = methods.get_body(request.body)
    if body[0] == False and body[1] != "empty":
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]
    if "user_admin" not in scope:
        return [result, content_type, 403]
    page = 0
    limit = 0
    offset = 0
    if "page" in body and "limit" in body:
        if isinstance(body["page"], int) and isinstance(body["limit"], int):
            page = body["page"]
            limit = body["limit"]
            offset = (limit*page) - limit
    
    with transaction.atomic():
        with connection.cursor() as cursor:
            sql = "SELECT id, username, name, phone, email, usersince_date, role, is_deleted FROM public.user ORDER BY id"
            if page > 0 and limit > 0:
                sql += " LIMIT {} OFFSET {}".format(limit, offset)
            cursor.execute(sql)
            row = database.dictfetchall(cursor)
            if len(row) == 0:
                cursor.close()
                return [result, content_type, 404]
            sql = "SELECT COUNT(*) as count FROM public.user"
            cursor.execute(sql)
            rowCount = database.dictfetchall(cursor)

    for user in row:
        user["usersince_date"] = methods.datetime_str(user["usersince_date"])
    
    result = methods.dumpJson({"totalCount": rowCount[0]["count"], "users": row})
    content_type = "application/json"
            
    return [result, content_type, statusCode]

def createUser(request):
    result = ""
    content_type = None
    statusCode = 201
    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]
    if not checkCreateUser(body):
        return [result, content_type, 400]
    with transaction.atomic():
        with connection.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO public.user (username, name, phone, email, usersince_date, role, is_deleted, client_id, password) VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s);",
                    [body["username"], body["name"], body["phone"], body["email"], methods.currentTime(), "user", methods.generate_client_id(), methods.hash_password(body["password"])])
            except IntegrityError:
                return [result, content_type, 409]
    return [result, content_type, statusCode]

def getClientId(request):
    result = ""
    content_type = None
    statusCode = 200 #401
    username = ""
    password = ""
    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]
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

def getToken(request):
    result = ""
    content_type = None
    statusCode = 200 #401
    if "client-id" in request.headers and "redirect-uri" in request.headers and "scope" in request.headers:
        if isinstance(request.headers["client-id"], str) and isinstance(request.headers["redirect-uri"], str) and isinstance(request.headers["scope"], str):
            client_id = request.headers["client-id"]
            redirect_uri = request.headers["redirect-uri"]
            scope = request.headers["scope"].split("+")
        else:
            return [result, content_type, 400]
    else: 
        return [result, content_type, 400]

    if redirect_uri != methods.getRedirect_uri():
        return [result, content_type, 401]

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, role, client_id FROM public.user WHERE client_id = %s AND is_deleted = 0", [client_id])
        row = database.dictfetchall(cursor)
        if len(row) == 1:
            if row[0]["client_id"] != client_id:
                return [result, content_type, 401]
        else:
            return [result, content_type, 401]
        role = row[0]["role"]
        user_id = row[0]["id"]
    if role == "admin":
        eglibible_scopes = methods.get_admin_scopes()
    else:
        eglibible_scopes = methods.get_user_scopes()

    for s in scope:
        if s not in eglibible_scopes:
            return [result, content_type, 403]

    content_type = "application/json"
    token = jwt.encode({'exp': datetime.utcnow() + timedelta(minutes=5), 'id': user_id, 'scope': " ".join(scope)}, settings.SECRET, algorithm='HS256')
    result = json.dumps({'access_token': token, 'token_type': "bearer", 'expires_in': 300})
    return [result, content_type, statusCode]



def updateUser(request, index):
    statusCode = 200 #401 403 404
    result = ""
    content_type = None
    #auth data
    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 401]
    scope = auth[1]["scope"]
    user_id = auth[1]["id"]
    
    if "user_admin" not in scope:
        if user_id != index:
            return [result, content_type, 403]
    #body data
    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]
    #update sql formation
    sql = "UPDATE public.user SET "
    sql_params = []
    if "name" in body:
        if not methods.is_word(body["name"], []) or len(body["name"]) > 20  or len(body["name"]) < 6:
            return [result, content_type, 400]
        sql += "name = %s, "
        sql_params.append(body["name"])
    if "phone" in body:
        if not methods.is_word(body["phone"], []) or len(body["phone"]) > 20  or len(body["phone"]) < 6:
            return [result, content_type, 400]
        sql += "phone = %s, "
        sql_params.append(body["phone"])
    if "email" in body:
        if not methods.is_word(body["email"], settings.EMAIL_CHARS) or not methods.is_email(body["email"]) or len(body["email"]) > 50  or len(body["email"]) < 6:
            return [result, content_type, 400]
        sql += "email = %s, "
        sql_params.append(body["email"])
    sql = sql[:-2]
    sql += " WHERE id = {}".format(index)
    #
    with transaction.atomic():
        cursor = connection.cursor()
        try:
            cursor.execute(sql, sql_params)
            cursor.execute("SELECT id, username, name, phone, email, usersince_date, role FROM public.user WHERE id = {} AND is_deleted = 0".format(index))
            row = database.dictfetchall(cursor)
        finally:
            cursor.close()

    row[0]["usersince_date"] = methods.datetime_str(row[0]["usersince_date"])
    content_type = "application/json"
    result = methods.dumpJson(row[0])
    return [result, content_type, statusCode]
    
def deleteUser(request, index):
    statusCode = 200 #401 403 404
    result = ""
    content_type = None
    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 401]
    scope = auth[1]["scope"]
    if "user_admin" not in scope:
        return [result, content_type, 403]
    with connection.cursor() as cursor:
        cursor.execute("UPDATE public.user SET is_deleted = 1 WHERE id = {} AND is_deleted = 0".format(index))
        if cursor.rowcount == 0:
            return [result, content_type, 404]
        cursor.execute("UPDATE public.ad SET is_deleted = 1 WHERE user_id = {}".format(index))
        
    return [result, content_type, statusCode]
    
def getUser(request, index):
    result = ""
    content_type = None
    statusCode = 200 #404
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username, name, phone, email, usersince_date, role FROM public.user WHERE id = %s", [index])
        row = database.dictfetchall(cursor)
        if len(row) != 1:
            cursor.close()
            return [result, content_type, 404]
    content_type = "application/json"
    row[0]["usersince_date"] = methods.datetime_str(row[0]["usersince_date"])
    result = methods.dumpJson(row[0])
    return [result, content_type, statusCode]

#Jei True - viskas gerai
def checkCreateUser(body):
    required_collumns = ["name", "username", "password", "phone", "email"]
    for collumn in required_collumns:
        if collumn not in body:
            return False
    if not methods.is_word(body["name"], []) or len(body["name"]) > 20 or len(body["name"]) < 2:
        return False
    if not methods.is_word(body["username"], []) or len(body["username"]) > 20 or len(body["username"]) < 6:
        return False
    if not methods.is_word(body["password"], settings.TEXT_CHARS) or len(body["password"]) > 50 or len(body["password"]) < 6:
        return False
    if not methods.is_word(body["phone"], []) or len(body["phone"]) > 20 or len(body["phone"]) < 6 :
        return False
    if not methods.is_word(body["email"], settings.EMAIL_CHARS) or not methods.is_email(body["email"])  or len(body["email"]) > 50 or len(body["phone"]) < 6:
        return False    
    return True
    

        
