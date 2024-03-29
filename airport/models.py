import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.last_name + " " + self.first_name

    class Meta:
        ordering = ["first_name"]


class Airport(models.Model):
    name = models.CharField(max_length=63, unique=True)
    closest_big_city = models.CharField(max_length=63, unique=True, blank=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departures",
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arrivals"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"Flight {self.source} - {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/airplanes/", filename)


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="airplanes"
    )
    image = models.ImageField(null=True, upload_to=airplane_image_file_path)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ManyToManyField(Airplane, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return (f"{str(self.route)}: "
                f"{self.departure_time} - {self.arrival_time}")


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, flight, airplane, error_to_raise):
        if airplane is not None:
            if not (1 <= row <= airplane.rows):
                raise error_to_raise(
                    {
                        "row": f"Row number must be in available range: "
                               f"(1, {airplane.rows})."
                    }
                )
            if not (1 <= seat <= airplane.seats_in_row):
                raise error_to_raise(
                    {
                        "seat": f"Seat number must be in available range: "
                                f"(1, {airplane.seats_in_row})."
                    }
                )

        if Ticket.objects.filter(flight=flight, row=row, seat=seat).exists():
            raise error_to_raise("This seat is already taken on this flight.")

    def clean(self):
        airplane = self.flight.airplane.all().first()
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight,
            airplane,
            ValidationError
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return (f"Ticket for Flight "
                f"{str(self.flight)} - Row: {self.row}, Seat: {self.seat}")

    class Meta:
        unique_together = ("row", "seat", "flight")
        ordering = ["row", "seat"]
