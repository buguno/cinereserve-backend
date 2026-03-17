from rest_framework.generics import ListAPIView

from showtimes.api.serializers import ShowtimeSerializer
from showtimes.models import Showtime


class ShowtimeListView(ListAPIView):
    serializer_class = ShowtimeSerializer

    def get_queryset(self):
        queryset = Showtime.objects.all().select_related('movie', 'room')
        movie_id = self.request.query_params.get('movie_id')

        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)

        return queryset.order_by('start_time')
