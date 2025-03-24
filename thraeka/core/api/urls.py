from core.api.views import TxnFile, TxnViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"txn", TxnViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("txnfile/", TxnFile.as_view(), name="txnfile"),
]
