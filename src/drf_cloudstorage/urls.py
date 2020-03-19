from rest_framework.routers import SimpleRouter

from drf_cloudstorage import views

router = SimpleRouter(trailing_slash=False)
router.register('', views.CloudFileViewSet)

urlpatterns = router.urls
