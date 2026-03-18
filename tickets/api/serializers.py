from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    Serializer,
    ValidationError,
)

from showtimes.api.serializers import ShowtimeSerializer
from tickets.models import Ticket


class TicketSerializer(ModelSerializer):
    showtime_details = ShowtimeSerializer(source='showtime', read_only=True)
    seat_details = CharField(source='seat.__str__', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'showtime',
            'seat',
            'purchased_at',
            'showtime_details',
            'seat_details',
        ]
        read_only_fields = ['purchased_at', 'user']

    def validate(self, data):
        if data['seat'].room != data['showtime'].room:
            raise ValidationError(
                "The selected seat does not belong to the showtime's room."
            )

        if Ticket.objects.filter(
            showtime=data['showtime'], seat=data['seat']
        ).exists():
            raise ValidationError('This seat has already been purchased.')

        return data


class CheckoutSerializer(Serializer):
    showtime_id = IntegerField()
    seat_id = IntegerField()
