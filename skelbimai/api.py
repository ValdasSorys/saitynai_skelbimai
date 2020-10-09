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
        resultDetails = createCategory(request, index)
    elif (request.method == 'GET'):
        resultDetails = getCategory(request, index)
    elif (request.method == 'DELETE'):
        resultDetails = deleteCategory(request, index)
    else:
        return HttpResponse(status = 404)
    return HttpResponse(resultDetails[0], content_type = resultDetails[1], status = resultDetails[2])

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

def updateCategory(request):
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

def getAdList(request):
    statusCode = 200
    result = Path('skelbimai/jsonmock/adList.json').read_text(encoding = 'utf-8')
    content_type = "application/json"
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
    

        
