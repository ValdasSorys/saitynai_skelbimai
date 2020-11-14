from django.urls import path

from . import categoryApi, adApi, commentApi, userApi

urlpatterns = [
    path('categories/', categoryApi.categoryAPI1, name='categoryAPI1'),
    path('categories/<int:index>/', categoryApi.categoryAPI2, name='categoryAPI2'),
    path('categories/<int:index>/ads/', adApi.adAPI1, name = "adAPI1"),
    path('ads/', adApi.adAPI2, name = "adAPI2"),
    path('ads/<int:index>/', adApi.adAPI3, name = "adAPI3"),
    path('ads/<int:index>/comments/', commentApi.commentAPI1, name = "commentAPI1"),
    path('ads/<int:index1>/comments/<int:index2>/', commentApi.commentAPI2, name = "commentAPI2"),
    path('users/', userApi.userAPI1, name = "userAPI1"),
    path('users/<int:index>/', userApi.userAPI2, name = "userAPI2"),
    path('users/login', userApi.userAPI3, name = "userAPI3"),
    path('users/gettoken', userApi.userAPI4, name = "userApi4"),
]