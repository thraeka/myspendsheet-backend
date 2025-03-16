from core.api.serializers import TxnSerializer
from core.api.services import TxnFileParser
from core.models import Txn
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


class Txn(ModelViewSet):
    """
    ViewSet to creating and editing Transactions
    """

    queryset = Txn.objects.all()
    serializer_class = TxnSerializer


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
