from django.shortcuts import render
from django.db import connection
from django.conf import settings
import jwt
import simplejson as json
from skelbimai import database, methods


# Create your views here.
from django.http import HttpResponse
from django.core import serializers
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt

#categories/<int:index>/ads
#GET - gauti tam tikros kategorijos skelbimų sąrašą
@csrf_exempt
def adAPI1(request, index):  
    if (request.method == 'GET'):
        resultDetails = getAdByCategoryList(request, index)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])

#ads/
#GET - gauti skelbimų sąrašą
#POST - sukurti skelbimą
@csrf_exempt
def adAPI2(request):  
    if (request.method == 'GET'):
        resultDetails = getAdList(request)
    elif (request.method == 'POST'):
        resultDetails = createAd(request)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])

#ads/<int:index>
#PUT - atnaujinti skelbimo informaciją
#GET - gauti vieno skelbimo informaciją
#DELETE - ištrinti skelbimą
@csrf_exempt
def adAPI3(request, index):  
    if (request.method == 'PUT'):
        resultDetails = updateAd(request, index)
    elif (request.method == 'GET'):
        resultDetails = getAd(request, index)
    elif (request.method == 'DELETE'):
        resultDetails = deleteAd(request, index)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])

def getAdList(request):
    statusCode = 200
    result = Path('skelbimai/jsonmock/adList.json').read_text(encoding = 'utf-8')
    content_type = "application/json"

    body = methods.get_body(request.body)
    if body[0] == False and body[1] != "empty":
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]

    page = 0
    limit = 0
    offset = 0
    if "page" in body and "limit" in body:
        if isinstance(body["page"], int) and isinstance(body["limit"], int):
            page = body["page"]
            limit = body["limit"]
            offset = (limit*page) - limit

    with connection.cursor() as cursor:
        sql = "SELECT * FROM public.ad WHERE is_deleted = 0 ORDER BY id ASC"
        if page > 0 and limit > 0:
            sql += " LIMIT {} OFFSET {}".format(limit, offset)
        cursor.execute(sql)
        row = database.dictfetchall(cursor)

        sql = "SELECT COUNT(*) as count FROM public.ad WHERE is_deleted = 0"
        cursor.execute(sql)
        rowCount = database.dictfetchall(cursor)
    for x in row:
        x["date"] = methods.datetime_str(x["date"])
    result = methods.dumpJson({"totalCount": rowCount[0]["count"],"ads": row})
    return [result, content_type, statusCode]

def getAdByCategoryList(request, index):
    statusCode = 200 #404
    result = Path('skelbimai/jsonmock/adList.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
    return [result, content_type, statusCode]
    
def createAd(request):
    statusCode = 201 #400 401 403 404
    result = ""
    content_type = None
    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 400]
    scope = auth[1]["scope"]
    user_id = auth[1]["id"]
    #body data
    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]
    if checkCreateAd(body) == False:
        return [result, content_type, 400]
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM public.category WHERE id = {}".format(body["category"]))
        categoryCount = database.dictfetchall(cursor)
        if categoryCount[0]["count"] != 1:
            cursor.close()
            return [result, content_type, 400]
        cursor.execute("INSERT INTO public.ad (name, text, category, price, date, user_id, is_deleted) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;", [body["name"], body["text"], body["category"], body["price"], methods.currentTime(), user_id, 0])
        ad_id = database.dictfetchall(cursor)
        cursor.execute("SELECT * FROM public.ad WHERE id = %s", [ad_id[0]["id"]])
        row = database.dictfetchall(cursor)
    row[0]["date"] = methods.datetime_str(row[0]["date"])
    content_type = "application/json"
    result = methods.dumpJson(row[0])
    return [result, content_type, statusCode]

def updateAd(request, index):
    statusCode = 200 #400 401 403 404
    result = ""
    content_type = None

    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 400]

    scope = auth[1]["scope"]
    user_id = auth[1]["id"]

    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]

    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]
    #update sql formation
    sql = "UPDATE public.ad SET "
    sql_params = []
    if "name" in body:
        if len(body["name"]) > 20  or len(body["name"]) < 6 or not methods.is_word(body["name"], [' ']):
            return [result, content_type, 400]
        sql += "name = %s, "
        sql_params.append(body["name"])
    if "text" in body:
        if len(body["text"]) > 5000  or len(body["text"]) < 6:
            return [result, content_type, 400]
        sql += "text = %s, "
        sql_params.append(body["text"])
    if "category" in body:
        if isinstance(body["category"], int) == False:
            return [result, content_type, 400]
        sql += "category = %s, "
        sql_params.append(body["category"])
    if "price" in body:
        if isinstance(body["price"], float) == False and isinstance(body["price"], float) == False:
            if body["price"] < 0:
                return [result, content_type, 400]
        sql += "price = %s, "
        sql_params.append(body["price"])
    sql = sql[:-2]
    sql += " WHERE id = {}".format(index)
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id FROM public.ad WHERE id = {} AND is_deleted = 0".format(index))
        rowCount = database.dictfetchall(cursor)
        print(rowCount)
        if len(rowCount) != 1:
            cursor.close()
            return [result, content_type, 404]
        if "user_admin" not in scope:
            if rowCount[0]["user_id"] != user_id:
                cursor.close()
                return [result, content_type, 403]
        if "category" in body:
            cursor.execute("SELECT Count(*) as count FROM public.category WHERE id = {}".format(body["category"]))
            rowCount = database.dictfetchall(cursor)
            if rowCount[0]["count"] != 1:
                cursor.close()
                return [result, content_type, 400]
        
        cursor.execute(sql, sql_params)
        cursor.execute("SELECT * FROM public.ad WHERE id = {}".format(index))
        row = database.dictfetchall(cursor)
        row[0]["date"] = methods.datetime_str(row[0]["date"])
        content_type = "application/json"
        result = methods.dumpJson(row[0])
    return [result, content_type, statusCode]

def getAd(request, index):
    statusCode = 200 #404
    content_type = None
    result = ""
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM public.ad WHERE id = {} AND is_deleted = 0".format(index))
        row = database.dictfetchall(cursor)
        if (len(row) == 0):
            cursor.close()
            return [result, content_type, 404]
    row[0]["date"] = methods.datetime_str(row[0]["date"])
    content_type = "application_json"
    result = methods.dumpJson(row[0])
    return [result, content_type, statusCode]

def deleteAd(request, index):
    statusCode = 200 #401 403 404
    result = ""
    content_type = None
    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 400]
    scope = auth[1]["scope"]
    user_id = auth[1]["id"]
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id FROM public.ad WHERE id = {}".format(index))
        row = database.dictfetchall(cursor)
        if "user_admin" not in scope:
            if user_id != row[0]["user_id"]:
                cursor.close()
                return [result, content_type, 403]
        row[0]["user_id"]
        cursor.execute("SELECT COUNT(*) as count FROM public.ad WHERE id = {}".format(index))
        rowCount = database.dictfetchall(cursor)
        if rowCount[0]["count"] != 1:
            cursor.close()
            return [result, content_type, 404]
        cursor.execute("UPDATE public.ad SET is_deleted = 1 WHERE id = {}".format(index))
    return [result, content_type, statusCode]

def checkCreateAd(body):
    if "name" not in body or "text" not in body or "category" not in body or "price" not in body:
        return False
    if len(body["name"]) > 20 or len(body["name"]) < 6 or not methods.is_word(body["name"], [' ']):
        return False
    if len(body["text"]) > 5000 or len(body["text"]) < 6:
        return False
    if isinstance(body["category"], int) == False:
        return False
    if isinstance(body["price"], float) == False and isinstance(body["price"], int) == False:
        if body["price"] < 0:
            return False
    return True
