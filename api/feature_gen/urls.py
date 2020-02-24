from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('api_server.urls')),
    path('admin/', admin.site.urls),
]
