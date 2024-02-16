from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from airport.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Order,
    Flight,
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    CrewSerializer,
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    OrderSerializer,
    FlightSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    OrderListSerializer,
    FlightDetailSerializer, AirplaneListSerializer, AirplaneImageSerializer,
)


class Pagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    pagination_class = Pagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    pagination_class = Pagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    pagination_class = Pagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        queryset = self.queryset

        if source:
            queryset = queryset.filter(source__name__icontains=source)

        if destination:
            queryset = queryset.filter(destination__name__icontains=destination)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source name (ex. ?source=Barc)"
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination name (ex. ?destination=Amst)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    pagination_class = Pagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    serializer_class = AirplaneSerializer
    pagination_class = Pagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related("route", "route__source", "route__destination")
        .prefetch_related("airplane")
        .annotate(
            tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    pagination_class = Pagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        queryset = self.queryset

        if departure_time:
            departure_time = datetime.strptime(departure_time, "%Y-%m-%d").date()
            queryset = self.queryset.filter(departure_time__date=departure_time)

        if arrival_time:
            arrival_time = datetime.strptime(arrival_time, "%Y-%m-%d").date()
            queryset = self.queryset.filter(arrival_time__date=arrival_time)

        if source:
            queryset = self.queryset.filter(route__source__name__icontains=source)

        if destination:
            queryset = self.queryset.filter(route__destination__name__icontains=destination)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.DATE,
                description="Filter by departure time (ex. ?departure_time=2024-02-15)"
            ),
            OpenApiParameter(
                "arrival_time",
                type=OpenApiTypes.DATE,
                description="Filter by arrival  time (ex. ?arrival_time=2024-02-15)"
            ),
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source name (ex. ?source=Barc)"
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination name (ex. ?destination=Amst)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
