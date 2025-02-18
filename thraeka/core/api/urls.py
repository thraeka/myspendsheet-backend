from django.urls import path
from core.api import views

urlpatterns = [
    path('transaction/<int:pk>/', views.SingleTransaction.as_view()),
]