from django.core.cache import cache
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from movies.api.serializers import MovieSerializer
from movies.models import Movie


class MovieListView(ListAPIView):
    queryset = Movie.objects.filter(is_active=True).order_by('release_date')
    serializer_class = MovieSerializer

    def list(self, request, *args, **kwargs):
        cache_key = 'movies:list'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60)

        return response
