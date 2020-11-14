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
    return [result, content_type, statusCode]

def updateAd(request, index):
    statusCode = 200 #400 401 403 404
    result = ""
    content_type = None
    return [result, content_type, statusCode]

def getAd(request, index):
    statusCode = 200 #404
    result = Path('skelbimai/jsonmock/ad.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
    return [result, content_type, statusCode]

def deleteAd(request, index):
    statusCode = 200 #401 403 404
    result = ""
    content_type = None
    return [result, content_type, statusCode]
