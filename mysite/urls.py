from django.contrib import admin
from django.urls import include, path
urlpatterns = [
    path('api/', include('skelbimai.urls')),
    path('admin/', admin.site.urls),
    path('test/', include('skelbimai.reactUrls')),
]