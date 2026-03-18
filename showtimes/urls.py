from django.urls import path

from showtimes.api.views import (
    ReserveSeatView,
    ShowtimeListView,
    ShowtimeSeatMapView,
)

urlpatterns = [
    path('', ShowtimeListView.as_view(), name='list_showtimes'),
    path(
        '<int:showtime_id>/seat-map/',
        ShowtimeSeatMapView.as_view(),
        name='seat_map',
    ),
    path(
        '<int:showtime_id>/reserve-seat/',
        ReserveSeatView.as_view(),
        name='reserve_seat',
    ),
]
