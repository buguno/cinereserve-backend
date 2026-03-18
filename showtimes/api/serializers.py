from rest_framework.serializers import (
    BooleanField,
    CharField,
    IntegerField,
    ModelSerializer,
    Serializer,
)

from movies.api.serializers import MovieSerializer
from showtimes.models import Room, Showtime


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity']


class ShowtimeSerializer(ModelSerializer):
    movie = MovieSerializer(read_only=True)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Showtime
        fields = ['id', 'movie', 'room', 'start_time']


class ReserveSeatSerializer(Serializer):
    seat_id = IntegerField()


class SeatMapSeatSerializer(Serializer):
    seat_id = IntegerField()
    row = CharField()
    number = IntegerField()
    status = CharField()
    is_locked_by_me = BooleanField()
    lock_ttl_seconds = IntegerField(allow_null=True)
