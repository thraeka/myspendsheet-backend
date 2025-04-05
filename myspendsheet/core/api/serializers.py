from core.models import Txn
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """

    class Meta:
        model = User
        fields = ["username", "password"]


class TxnSerializer(serializers.ModelSerializer):
    """
    Serializer for Txn model.
    """

    class Meta:
        model = Txn
        exclude = ["user"]


class SummarySerializer(serializers.Serializer):
    """
    Serializer for Summary
    """

    date_range = serializers.ListField(child=serializers.DateField())
    total = serializers.DecimalField(max_digits=9, decimal_places=2)
    total_by_cat = serializers.DictField(
        child=serializers.DecimalField(max_digits=9, decimal_places=2)
    )
