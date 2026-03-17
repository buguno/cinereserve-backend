from rest_framework.serializers import ModelSerializer

from movies.models import Movie


class MovieSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            'id',
            'title',
            'description',
            'duration_minutes',
            'release_date',
        ]
