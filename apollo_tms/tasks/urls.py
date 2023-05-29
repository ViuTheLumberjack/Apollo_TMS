from django.urls import path

from . import views

urlpatterns = [
    path('api/v1/tasks/', views.TaskViewSet.as_view()),
    path('api/v2/tasks/', views.TaskViewSet.as_view()),
]