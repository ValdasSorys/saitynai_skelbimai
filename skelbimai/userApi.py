from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.core import serializers
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt

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

    
def getUserList(request):
    statusCode = 200 #403
    result = Path('skelbimai/jsonmock/userList.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
    return [result, content_type, statusCode]

def createUser(request):
    statusCode = 201 #400
    result = ""
    content_type = None
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
    

        
