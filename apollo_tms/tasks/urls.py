from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'collections', views.CollectionViewSet, basename='collection')
router.register(r'collections/(?P<collection_id>\d+)/tasks', views.TaskViewSet)
router.register(r'tasks', views.TaskViewSet, basename='task')

urlpatterns = router.urls