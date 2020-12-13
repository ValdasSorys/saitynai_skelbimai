from django.urls import path

from . import reactApp

urlpatterns = [
    path('', reactApp.reactAppRender, name='reactAppRender'),
]