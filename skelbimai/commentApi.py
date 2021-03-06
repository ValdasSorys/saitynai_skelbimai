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
import psycopg2

#ads/<int:index>/comments/
#GET - gauti visų skelbimo komentarų sąrašą
#POST - sukurti komentarą skelbimui
@csrf_exempt
def commentAPI1(request, index):  
    if (request.method == 'GET'):
        resultDetails = getCommentList(request, index)
    elif (request.method == 'POST'):
        if "actualMethod" in request.GET and request.GET["actualMethod"] == "GET/":
            resultDetails = getCommentList(request, index)
        else:
            resultDetails = createComment(request, index)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])

#ads/<int:index1>/comments/<int:index2>
#PUT - pakeisti skelbimo vieno komentaro tekstą
#GET - gauti vieną skelbimo komentarą
#DELETE - pašalinti vieną skelbimo komentarą
@csrf_exempt
def commentAPI2(request, index1, index2):  
    if (request.method == 'PUT'):
        resultDetails = updateComment(request, index1, index2)
    elif (request.method == 'GET'):
        resultDetails = getComment(request, index1, index2)
    elif (request.method == 'DELETE'):
        resultDetails = deleteComment(request, index1, index2)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])

def getCommentList(request, index):
    statusCode = 200 #404
    result = ""
    content_type = ""

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
        else:
            return [result, content_type, 400]

    with transaction.atomic():
        with connection.cursor() as cursor:
            sql = "SELECT public.comment.user_id, public.comment.ad_id, public.comment.date, public.comment.text, comment_id, userWriter.username as username, ad.user_id as idowner "\
                    "FROM public.comment "\
                    "INNER JOIN public.user AS userWriter ON public.comment.user_id = userWriter.id "\
                    "INNER JOIN public.ad AS ad ON public.comment.ad_id = ad.id "\
                    "INNER JOIN public.user AS userOwner ON ad.user_id = userOwner.id "\
                    "WHERE public.comment.ad_id = %s ORDER BY comment_id DESC"
            if page > 0 and limit > 0:
                sql += " LIMIT {} OFFSET {}".format(limit, offset)
            cursor.execute(sql, [index])
            row = database.dictfetchall(cursor)
            cursor.execute("SELECT Count(*) as count FROM public.comment WHERE ad_id = %s", [index])
            rowCount = database.dictfetchall(cursor)
            if rowCount[0]["count"] == 0:
                return [result, content_type, 404]
    for r in row:
        r["date"] = methods.datetime_str(r["date"])
    result = methods.dumpJson({"totalCount": rowCount[0]["count"],"comments": row})
    content_type = "application/json"

    return [result, content_type, statusCode]

def createComment(request, index):
    statusCode = 201 #400 401 404
    result = ""
    content_type = None
    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 401]
    scope = auth[1]["scope"]
    user_id = auth[1]["id"]
    if "comments" not in scope:
        return [result, content_type, 403]
    
    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]
    if "text" not in body or len(body["text"]) > 300 or len(body["text"]) < 1:
        return [result, content_type, 400]
    
    with transaction.atomic():
        with connection.cursor() as cursor:
            insert_success = False
            for x in range(100):
                try:
                    cursor.execute("INSERT INTO public.comment (user_id, ad_id, date, text, comment_id) VALUES (%s, %s, %s, %s, "+
                    "(SELECT coalesce(max(comment_id),0) + 1  FROM public.comment WHERE ad_id= %s)) RETURNING comment_id", 
                    [user_id, index, methods.currentTime(), body["text"], index])
                    insert_success = True
                    break
                except IntegrityError as e:
                    print(e)
                    if "Key (ad_id)" in str(e):
                        return [result, content_type, 404]
                    if "Key (ad_id, comment_id)" in str(e):
                        continue
                    break
            if not insert_success:
                return [result, content_type, 500]       
            row_comment_id = database.dictfetchall(cursor)
            cursor.execute("SELECT *, (SELECT name FROM public.user WHERE id = %s) as user_name FROM public.comment WHERE ad_id = %s AND comment_id = %s", [user_id, index, row_comment_id[0]["comment_id"]])
            row = database.dictfetchall(cursor)
        
    row[0]["date"] = methods.datetime_str(row[0]["date"])
    result = methods.dumpJson(row[0])
    content_type = "application/json"
    
        
    return [result, content_type, statusCode]
    
def updateComment(request, index1, index2):
    statusCode = 200 #400 401 403 404
    result = ""
    content_type = None

    ad_index = index1
    comment_index = index2

    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 401]
    scope = auth[1]["scope"]
    user_id = auth[1]["id"]

    body = methods.get_body(request.body)
    if body[0] == False:
        return [result, content_type, 400]
    body_empty = body[0]
    body = body[1]

    if "text" not in body or len(body["text"]) > 300 or len(body["text"]) < 1:
        return [result, content_type, 400]

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_deleted FROM public.ad WHERE id = %s", [ad_index])
            row = database.dictfetchall(cursor)
            if len(row) != 1 or row[0]["is_deleted"] == 1:
                cursor.close()
                return [result, content_type, 404]
            cursor.execute("SELECT user_id FROM public.comment WHERE ad_id = %s AND comment_id = %s", [ad_index, comment_index])
            row = database.dictfetchall(cursor)
            if len(row) != 1:
                return [result, content_type, 404]
            if "comments_admin" not in scope:
                if "comments" not in scope or row[0]["user_id"] != user_id:
                    return [result, content_type, 403]

            cursor.execute("UPDATE public.comment SET text = %s, date = %s WHERE ad_id = %s AND comment_id = %s", [body["text"], methods.currentTime(), ad_index, comment_index])
            if cursor.rowcount == 0:
                return [result, content_type, 404]
            sql = "SELECT public.comment.user_id, public.comment.ad_id, public.comment.date, public.comment.text, comment_id, userWriter.username as username, ad.user_id as idowner "\
                    "FROM public.comment "\
                    "INNER JOIN public.user AS userWriter ON public.comment.user_id = userWriter.id "\
                    "INNER JOIN public.ad AS ad ON public.comment.ad_id = ad.id "\
                    "INNER JOIN public.user AS userOwner ON ad.user_id = userOwner.id "\
                    "WHERE public.comment.ad_id = %s AND public.comment.comment_id = %s ORDER BY comment_id DESC"
            cursor.execute( sql, [ad_index, comment_index])
            row = database.dictfetchall(cursor)

    row[0]["date"] = methods.datetime_str(row[0]["date"])
    result = methods.dumpJson(row[0])
    content_type = "application/json"
    return [result, content_type, statusCode]

def getComment(request, index1, index2):
    statusCode = 200 #404
    result = ""
    content_type = ""
    ad_index = index1
    comment_index = index2
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_deleted FROM public.ad WHERE id = %s", [ad_index])
            row = database.dictfetchall(cursor)
            if len(row) == 0 or row[0]["is_deleted"] == 1:
                cursor.close()
                return [result, content_type, 404]
            cursor.execute("SELECT * FROM public.comment WHERE ad_id = %s AND comment_id = %s", [ad_index, comment_index])
            row = database.dictfetchall(cursor)
            if len(row) != 1:
                cursor.close()
                return [result, content_type, 404]
            cursor.execute("SELECT name FROM public.user WHERE id = %s", [row[0]["user_id"]])
            row_user_name = database.dictfetchall(cursor) 
    row[0]["date"] = methods.datetime_str(row[0]["date"])
    row[0]["user_name"] = row_user_name[0]["name"]
    result = methods.dumpJson(row[0])
    content_type = "application/json"
    return [result, content_type, statusCode]
    
def deleteComment(request, index1, index2):
    statusCode = 200 #401 403 404
    result = ""
    content_type = None

    ad_index = index1
    comment_index = index2

    if "Authorization" in request.headers:
        auth = methods.decode_token(request.headers["Authorization"])
        if auth[0] == False:
            return [result, content_type, 401]
    else:
        return [result, content_type, 401]
    scope = auth[1]["scope"]
    user_id = auth[1]["id"]
    #if "comments_admin" not in scope:
    #    return [result, content_type, 403]
    
    with transaction.atomic():
        with connection.cursor() as cursor:            
            cursor.execute("SELECT user_id FROM public.comment WHERE ad_id = %s AND comment_id = %s", [ad_index, comment_index])
            row = database.dictfetchall(cursor)
            if len(row) == 0:
                return [result, content_type, 404]
            if "comments_admin" not in scope:
                if row[0]["user_id"] != user_id:
                    return [result, content_type, 403]
            cursor.execute("DELETE FROM public.comment WHERE ad_id = %s AND comment_id = %s", [ad_index, comment_index])
            if cursor.rowcount == 0:
                return [result, content_type, 404]
    return [result, content_type, statusCode]
        
