from core.api.serializers import TxnSerializer
from core.api.services import TxnFileParser
from core.models import Txn
from django.http import Http404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView


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


class TxnFile(APIView):
    """
    Upload a file to be parsed for transactions
    """

    parser = (MultiPartParser, FormParser)

    def __init__(self):
        self.parser = TxnFileParser()
        super().__init__()

    def post(self, request, *args, **kwargs):
        txn_file_dict = self.parser.txn_file_to_dict(request.data.get("file"))
        serializer = TxnSerializer(data=txn_file_dict, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
