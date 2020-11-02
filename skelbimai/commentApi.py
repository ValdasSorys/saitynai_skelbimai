from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.core import serializers
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt

#ads/<int:index>/comments/
#GET - gauti visų skelbimo komentarų sąrašą
#POST - sukurti komentarą skelbimui
@csrf_exempt
def commentAPI1(request, index):  
    if (request.method == 'GET'):
        resultDetails = getCommentList(request, index)
    elif (request.method == 'POST'):
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
    result = Path('skelbimai/jsonmock/comments.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
    return [result, content_type, statusCode]

def createComment(request, index):
    statusCode = 201 #400 401 404
    result = ""
    content_type = None
    return [result, content_type, statusCode]
    
def updateComment(request, index1, index2):
    statusCode = 200 #400 401 403 404
    result = ""
    content_type = None
    return [result, content_type, statusCode]

def getComment(request, index1, index2):
    statusCode = 200 #404
    result = Path('skelbimai/jsonmock/comment.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
    return [result, content_type, statusCode]
    
def deleteComment(request, index1, index2):
    statusCode = 200 #401 403 404
    result = ""
    content_type = None
    return [result, content_type, statusCode]
        
