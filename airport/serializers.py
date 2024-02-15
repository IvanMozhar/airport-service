from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from airport.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Order,
    Ticket,
    Flight
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(serializers.ModelSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    airplane_capacity = serializers.IntegerField(
        source="capacity",
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "airplane_capacity",
            "tickets_available"
        )


class AirplaneNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("name",)


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField(many=False)
    airplane = AirplaneNameSerializer(many=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    airplane = AirplaneSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(many=False, read_only=True)

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seats_in_row"],
            attrs["flight"],
            attrs["flight"].airplane.all().first(),
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = FlightSerializer(many=False, read_only=True)


class TicketSeatSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)