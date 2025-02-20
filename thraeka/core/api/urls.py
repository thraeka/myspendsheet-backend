from django.urls import path
from core.api import views

urlpatterns = [
    path('transaction/', views.NewTransaction.as_view()),
    path('transaction/<int:pk>/', views.ExistingTransaction.as_view()),
]