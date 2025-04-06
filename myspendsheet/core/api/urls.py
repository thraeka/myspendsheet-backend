from core.api.views import CreateUserView, SummaryView, TxnFile, TxnViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"txn", TxnViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("signup/", CreateUserView.as_view(), name="signup"),
    path("signin/", TokenObtainPairView.as_view(), name="signin"),
    path("signin/refresh/", TokenRefreshView.as_view(), name="signin_refresh"),
    # TODO: Create logout api and handle old tokens
    path("txnfile/", TxnFile.as_view(), name="txnfile"),
    path(
        "summary/<str:start_date>/<str:end_date>", SummaryView.as_view(), name="summary"
    ),
]
