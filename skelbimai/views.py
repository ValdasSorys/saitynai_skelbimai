from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.core import serializers
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):  
    if (request.method == 'GET'):
        resultDetails = api1(request)
    if (request.method == 'POST'):
        result = Path('skelbimai/test.json').read_text()
        statusCode = 599
        resultDetails = [result, statusCode]
        #resultDetails = api1(request)
    if (request.method == 'PUT'):
        result = Path('skelbimai/test.json').read_text()    
    if (request.method == 'DELETE'):
        result = Path('skelbimai/test.json').read_text()
    return HttpResponse(resultDetails[0], content_type="application/json", status = resultDetails[1])
    
def api1(request):
    statusCode = 201
    result = Path('skelbimai/test.json').read_text()
    return [result, statusCode]
    