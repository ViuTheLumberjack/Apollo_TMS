from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()

router.register(r'groups', views.GroupViewSet)
router.register(r'groups/(?P<group_id>\d+)/members', views.GroupMembersViewSet, basename='group-members')
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include('dj_rest_auth.urls'), name='login'),
    path('registration/', include('dj_rest_auth.registration.urls'), name='registration'),
    path('', include(router.urls)),
]