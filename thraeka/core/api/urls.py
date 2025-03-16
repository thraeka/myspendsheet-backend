from core.api.views import Txn, TxnFile
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"txn", Txn)

urlpatterns = [
    path("", include(router.urls)),
    path("txnfile/", TxnFile.as_view(), name="txnfile"),
]
