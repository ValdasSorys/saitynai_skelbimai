from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.core import serializers
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):  
    if (request.method == 'GET'):
        result = Path('skelbimai/test.json').read_text()
    else:
        result = "null"
    return HttpResponse(result, content_type="application/json", status = 201)