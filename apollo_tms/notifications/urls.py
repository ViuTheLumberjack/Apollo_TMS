from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import NotificationView

router = SimpleRouter()
router.register('notifications', NotificationView, basename='notifications')

urlpatterns = router.urls