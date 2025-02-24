from core.models import Txn
from core.api.serializers import TxnSerializer
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class NewTxn(APIView):
    """
    Post a Txn instance.
    """
    def post(self, request, format=None):
        serializer = TxnSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExistingTxn(APIView):
    """
    Retrieve, update, or delete an existing Txn instance.
    """
    def get_object(self, pk):
        try:
            return Txn.objects.get(pk=pk)
        except Txn.DoesNotExist:
            raise Http404
        
        
    def get(self, request, pk, format=None):
        Txn = self.get_object(pk)
        serializer = TxnSerializer(Txn)
        return Response(serializer.data)
    

    def put(self, request, pk, format=None):
        Txn = self.get_object(pk)
        serializer = TxnSerializer(Txn, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, pk, format=None):
        Txn = self.get_object(pk)
        Txn.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    