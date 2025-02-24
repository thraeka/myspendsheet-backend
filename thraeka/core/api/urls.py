from django.urls import path
from core.api import views

urlpatterns = [
    path('txn/', views.NewTxn.as_view(),name='txn'),
    path('txn/<int:pk>/', views.ExistingTxn.as_view(), name='txn_mod'),
]