from core.api.serializers import TxnSerializer
from core.api.services import TxnFileParser
from core.models import Txn
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


class TxnViewSet(ModelViewSet):
    """
    ViewSet for CRUD txn

    For bulk txn:
        - can handle filtering by date and amount.
        - can order by amount and date.

    TODO:
        - add pagination
    """

    queryset = Txn.objects.all()
    serializer_class = TxnSerializer
    filter_backend = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "amount": ["exact", "gte", "lte"],
        "date": ["exact", "gte", "lte"],
    }
    ordering_fields = ["amount", "date"]
    ordering = ["-date"]


class TxnFile(APIView):
    """
    API endpoint for uploading a file to be parsed for tnn.

    The uploaded file is processed and parsed into txn data which is serialized and saved into db

    Method:
        post: Handles file upload and txn creation

    TODO:
        - currently only handles bank statement pdf. adding more formats in future
        - need to add format type checking
    """

    parser = (MultiPartParser, FormParser)

    def __init__(self):
        """
        Init the TxnFile API view with a file parser
        """
        self.parser = TxnFileParser()
        super().__init__()

    def post(self, request, *args, **kwargs):
        """
        Handles POST request for uploading and parsing txn files

        Args:
            request (Request): The HTTP request wtih txn file
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: Response obj with serialized txn data or error
        """
        txn_file_dict = self.parser.txn_file_to_dict(request.data.get("file"))
        serializer = TxnSerializer(data=txn_file_dict, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
