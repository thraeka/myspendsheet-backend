from core.api.views import CreateUserView, SummaryView, TxnFile, TxnViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"txn", TxnViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("signup/", CreateUserView.as_view(), name="signup"),
    path("txnfile/", TxnFile.as_view(), name="txnfile"),
    path(
        "summary/<str:start_date>/<str:end_date>", SummaryView.as_view(), name="summary"
    ),
]
