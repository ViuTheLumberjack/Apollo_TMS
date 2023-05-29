from django.urls import path, include

from . import views

urlpatterns = [
    path('api/v1/', include('dj_rest_auth.urls')),
    path('api/v1/registration/', include('dj_rest_auth.registration.urls'))
]