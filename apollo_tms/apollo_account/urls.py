from django.urls import path, include

from . import views

urlpatterns = [
    path('', include('dj_rest_auth.urls'), name='login'),
    path('registration/', include('dj_rest_auth.registration.urls'), name='registration'),
]