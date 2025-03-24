from core.models import Txn
from rest_framework import serializers


class TxnSerializer(serializers.ModelSerializer):
    """
    Serializer for Txn model.
    """

    class Meta:
        model = Txn
        fields = "__all__"
