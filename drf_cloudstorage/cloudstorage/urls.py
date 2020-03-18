from rest_framework.routers import SimpleRouter

from cloudstorage import views

router = SimpleRouter(trailing_slash=False)
router.register('', views.CloudFileViewSet)

urlpatterns = router.urls
