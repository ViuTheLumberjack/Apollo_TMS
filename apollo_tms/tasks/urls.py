from rest_framework import routers
from django.urls import path

from . import views

router = routers.SimpleRouter()
router.register(r'collection', views.CollectionViewSet, basename='collection')
router.register(r'collection/(?P<collection_id>\d+)/tasks', views.TaskViewSet)

urlpatterns = [
    path('tasks', views.PersonalTasksView.as_view(), name='personal_tasks'),
] + router.urls