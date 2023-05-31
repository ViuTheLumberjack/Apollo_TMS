from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'tasks', views.TaskViewSet)

urlpatterns = router.urls