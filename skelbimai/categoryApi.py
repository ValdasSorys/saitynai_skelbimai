from django.shortcuts import render

# Create your views here.
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
    result = Path('skelbimai/jsonmock/categoryList.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
    return [result, content_type, statusCode]
    
def createCategory(request):
    statusCode = 201 #400 401 403 409
    result = ""
    content_type = None
    return [result, content_type, statusCode]

def updateCategory(request, index):
    statusCode = 200 #400 401 403 404
    result = ""
    content_type = None
    return [result, content_type, statusCode]

def getCategory(request, index):
    statusCode = 200 #404
    result = Path('skelbimai/jsonmock/category.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
    return [result, content_type, statusCode]
    
def deleteCategory(request, index):
    statusCode = 200 #401 403 404
    result = ""
    content_type = None
    return [result, content_type, statusCode]