from django.urls import path
from . import views

urlpatterns = [
    path('api/execute/', views.Execute.as_view()),
    path('specs/', views.Specs.as_view()),
    path('authentication-token/', views.AuthenticationToken.as_view()),
    path('save/', views.Save.as_view()),
    path('admin/', admin.site.urls),
]

