from django.urls import path

from . import views

urlpatterns = [
    path('categories/', views.categoryAPI1, name='categoryAPI1'),
    path('categories/<int:index>', views.categoryAPI2, name='categoryAPI2'),
]