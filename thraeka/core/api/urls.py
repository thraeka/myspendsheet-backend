from core.api import views
from django.urls import path

urlpatterns = [
    path("txn/", views.NewTxn.as_view(), name="txn"),
    path("txn/<int:pk>/", views.ExistingTxn.as_view(), name="txn_mod"),
    path("txnfile/", views.TxnFile.as_view(), name="txnfile"),
]
