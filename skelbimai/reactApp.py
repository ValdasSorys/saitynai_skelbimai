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
from datetime import datetime, timedelta

@csrf_exempt
def reactAppRender(request):  
    return render(request, 'frontend/public/index.html')

        
