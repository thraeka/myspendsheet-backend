from core.api.views import CreateUserView, SummaryView, TxnFile, TxnViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"txn", TxnViewSet, basename="txn")

urlpatterns = [
    path("", include(router.urls)),
    path("user/", CreateUserView.as_view(), name="user"),
    # TODO: Create endpoint to retrieve, update, and destroy auth user
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # TODO: Create endpoint to handle old tokens
    path("txnfile/", TxnFile.as_view(), name="txnfile"),
    path(
        "summary/<str:start_date>/<str:end_date>", SummaryView.as_view(), name="summary"
    ),
]
