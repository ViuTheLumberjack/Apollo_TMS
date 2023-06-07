from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()

router.register(r'group', views.GroupViewSet)
router.register(r'group/(?P<group_id>\d+)/member', views.GroupMembersViewSet, basename='group-members')
router.register(r'user', views.UserViewSet)

urlpatterns = [
    path('', include('dj_rest_auth.urls'), name='login'),
    path('registration/', include('dj_rest_auth.registration.urls'), name='registration'),
    path('', include(router.urls)),
]