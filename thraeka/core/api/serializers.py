from rest_framework import serializers
from core.models import Txn

class TxnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Txn
        fields = '__all__'
