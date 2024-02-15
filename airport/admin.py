from django.contrib import admin

from models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Order,
    Flight,
    Ticket
)

admin.register(Crew)
admin.register(Airport)
admin.register(Route)
admin.register(AirplaneType)
admin.register(Airplane)
admin.register(Order)
admin.register(Flight)
admin.register(Ticket)
