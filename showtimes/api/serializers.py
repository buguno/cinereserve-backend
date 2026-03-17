from rest_framework.serializers import ModelSerializer

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
