from rest_framework.generics import ListAPIView

from movies.api.serializers import MovieSerializer
from movies.models import Movie


class MovieListView(ListAPIView):
    queryset = Movie.objects.filter(is_active=True).order_by('release_date')
    serializer_class = MovieSerializer
