from django.urls import path
from . import views

urlpatterns = [
    path('specs/', views.Specs.as_view()),
    path('authentication-token/', views.AuthenticationToken.as_view()),
]

