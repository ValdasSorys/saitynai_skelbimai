from django.urls import path

from . import api

urlpatterns = [
    path('categories/', api.categoryAPI1, name='categoryAPI1'),
    path('categories/<int:index>', api.categoryAPI2, name='categoryAPI2'),
    path('categories/<int:index>/ads', api.adAPI1, name = "adAPI1"),
    path('ads/', api.adAPI2, name = "adAPI2"),
    path('ads/<int:index>', api.adAPI3, name = "adAPI3"),
    path('ads/<int:index>/comments/', api.commentAPI1, name = "commentAPI1"),
    path('ads/<int:index1>/comments/<int:index2>', api.commentAPI2, name = "commentAPI2"),
    path('users/', api.userAPI1, name = "userAPI1"),
    path('users/<int:index>/', api.userAPI2, name = "userAPI2"),
]