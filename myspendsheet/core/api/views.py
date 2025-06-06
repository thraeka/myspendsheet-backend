from datetime import datetime

from core.api.serializers import SummarySerializer, TxnSerializer, UserSerializer
from core.api.services import SummaryCache, TxnFileParser
from core.models import Txn
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


class CreateUserView(CreateAPIView):
    """
    API view to create user

    TODO:
        - add throttling (please dont ddos me)
        - setup unique email
        - password reset
        - captcha
    """

    serializer_class = UserSerializer


class TxnViewSet(ModelViewSet):
    """
    ViewSet for CRUD txn

    For bulk txn:
        - can handle filtering by date and amount.
        - can order by amount and date.

    TODO:
        - add pagination
    """

    serializer_class = TxnSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "amount": ["exact", "gte", "lte"],
        "date": ["exact", "gte", "lte"],
    }
    ordering_fields = ["amount", "date"]
    ordering = ["-date"]
    permission_classes = [IsAuthenticated]

    summary_cache = SummaryCache()

    def get_queryset(self):
        return self.request.user.txns.all()

    def perform_create(self, serializer: TxnSerializer) -> None:
        """Create a new txn and update the summary cache"""
        serializer.save(user=self.request.user)
        self.summary_cache.update(
            self.request.user,
            serializer.validated_data["date"],
            serializer.validated_data["amount"],
            serializer.validated_data["category"],
        )

    def perform_update(self, serializer: TxnSerializer) -> None:
        """Update an existing txn and update the summary cache"""
        # Update summary cache to remove old txn values
        # TO DO: Update logic to remove two cache access
        self.summary_cache.update(
            self.request.user,
            serializer.instance.date,
            -1 * serializer.instance.amount,
            serializer.instance.category,
        )
        serializer.save(user=self.request.user)
        # Update summary cache to add new txn values
        self.summary_cache.update(
            self.request.user,
            serializer.instance.date,
            serializer.instance.amount,
            serializer.instance.category,
        )

    def perform_destroy(self, instance: Txn) -> None:
        """Delete txn from DB and update the summary cache"""
        instance.delete()
        self.summary_cache.update(
            self.request.user, instance.date, -1 * instance.amount, instance.category
        )


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
    permission_classes = [IsAuthenticated]

    def __init__(self):
        """
        Init the TxnFile API view with a file parser
        """
        self.parser = TxnFileParser()
        super().__init__()

    def post(self, request: Request, *args, **kwargs) -> Response:
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
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SummaryView(APIView):
    """
    API endpoint that returns txn summary of a specified date range

    Method:
        Public:
            - GET HTTP method to return txn summary of specified date range

    To Do:
        - better error checking ie date range
    """

    permission_classes = [IsAuthenticated]

    summary_cache = SummaryCache()

    def get(self, request: Request, start_date: str, end_date: str) -> Response:
        """Handle GET request to return txn summary for the specified date range"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        summary_data = self.summary_cache.get(request.user, start, end)
        serializer = SummarySerializer(data=summary_data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
