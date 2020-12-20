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

#categories/
#GET - gauti kategorijų sąrašą
#POST - sukurti kategoriją
@csrf_exempt
def categoryAPI1(request):  
    if (request.method == 'GET'):
        resultDetails = getCategoryList(request)
    elif (request.method == 'POST'):
        resultDetails = createCategory(request)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])

#categories/<int:index>
#PUT - pakeisti kategorijos pavadinimą
#GET - gauti kategorijos informaciją (pavadinimą)
#DELETE - ištrinti kategoriją
@csrf_exempt
def categoryAPI2(request, index):  
    if (request.method == 'PUT'):
        resultDetails = updateCategory(request, index)
    elif (request.method == 'GET'):
        resultDetails = getCategory(request, index)
    elif (request.method == 'DELETE'):
        resultDetails = deleteCategory(request, index)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])
    
def getCategoryList(request):
    statusCode = 200
    result = ""
    content_type = ""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM public.category ORDER BY name")
        row = database.dictfetchall(cursor)
    if (len(row) == 0):
        return [result, content_type, 404]
    result = methods.dumpJson(row)
    content_type = "application/json"
    return [result, content_type, statusCode]
    
def createCategory(request):
    statusCode = 201 #400 401 403 409
    result = ""
    content_type = None
    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 401]
    scope = auth[1]["scope"]
    if "categories_admin" not in scope:
        return [result, content_type, 403]
    
    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]

    if "name" not in body:
        return [result, content_type, 400]
    if len(body["name"]) > 20 or len(body["name"]) < 2:
        return [result, content_type, 400]
    with connection.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO public.category (name) VALUES(%s) RETURNING id", [body["name"]])
        except:
            return [result, content_type, 409]
        category_id = database.dictfetchall(cursor)
    result = methods.dumpJson({"id": category_id[0]["id"], "name": body["name"]})
    content_type = "application/json"
    return [result, content_type, statusCode]

def updateCategory(request, index):
    statusCode = 200 #400 401 403 404
    result = ""
    content_type = None
    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 401]
    scope = auth[1]["scope"]

    if "categories_admin" not in scope:
        return [result, content_type, 403]

    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]

    if "name" not in body:
        return [result, content_type, 400]
    if len(body["name"]) > 20 or len(body["name"]) < 2:
        return [result, content_type, 400]
    
    with connection.cursor() as cursor:
        try:
            cursor.execute("UPDATE public.category SET name = %s WHERE id = %s", [body["name"], index])
        except IntegrityError:
            return [result, content_type, 409]
        if cursor.rowcount == 0:
            return [result, content_type, 404]

    result = methods.dumpJson({"id": index, "name": body["name"]})
    content_type = "application_json"        
    return [result, content_type, statusCode]

def getCategory(request, index):
    statusCode = 200 #404
    result = ""
    content_type = None
    with connection.cursor() as cursor:
        sql = "SELECT * FROM public.category WHERE id = {}".format(index)
        cursor.execute(sql)
        row = database.dictfetchall(cursor)
    if len(row) != 1:
        return [result, content_type, 404]
    result = methods.dumpJson(row[0])
    content_type = "application/json"
    return [result, content_type, statusCode]
    
def deleteCategory(request, index):
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
    if "categories_admin" not in scope:
        return [result, content_type, 403]
    with connection.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM public.category WHERE id = {}".format(index))
        except IntegrityError:
            return [result, content_type, 409]
        if cursor.rowcount == 0:
            return [result, content_type, 404]
    return [result, content_type, statusCode]