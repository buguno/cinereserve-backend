from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from showtimes.api.serializers import (
    ReserveSeatSerializer,
    SeatMapSeatSerializer,
    ShowtimeSerializer,
)
from showtimes.models import Seat, Showtime
from showtimes.services import (
    acquire_seat_lock,
    get_locked_seats,
    get_seat_lock_owner,
    get_seat_lock_ttl,
)
from tickets.models import Ticket


class ShowtimeListView(ListAPIView):
    serializer_class = ShowtimeSerializer

    def get_queryset(self):
        queryset = Showtime.objects.all().select_related('movie', 'room')
        movie_id = self.request.query_params.get('movie_id')

        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)

        return queryset.order_by('start_time')

    def list(self, request, *args, **kwargs):
        movie_id = request.query_params.get('movie_id', 'all')
        cache_key = f'showtimes:list:{movie_id}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60)

        return response


class ShowtimeSeatMapView(APIView):
    def get(self, request, showtime_id: int):
        showtime = get_object_or_404(
            Showtime.objects.select_related('room'),
            pk=showtime_id,
        )
        seats = showtime.room.seats.all().order_by('row', 'number')
        purchased_seat_ids = set(
            Ticket.objects.filter(showtime=showtime).values_list(
                'seat_id', flat=True
            )
        )
        locked_seats = get_locked_seats(showtime.id)
        user_id = (
            str(request.user.id) if request.user.is_authenticated else None
        )
        data = []
        for seat in seats:
            if seat.id in purchased_seat_ids:
                status_value = 'purchased'
                lock_ttl = None
                is_locked_by_me = False
            elif seat.id in locked_seats:
                status_value = 'reserved'
                lock_ttl = get_seat_lock_ttl(showtime.id, seat.id)
                is_locked_by_me = locked_seats[seat.id] == user_id
            else:
                status_value = 'available'
                lock_ttl = None
                is_locked_by_me = False
            data.append({
                'seat_id': seat.id,
                'row': seat.row,
                'number': seat.number,
                'status': status_value,
                'is_locked_by_me': is_locked_by_me,
                'lock_ttl_seconds': lock_ttl,
            })
        serializer = SeatMapSeatSerializer(data, many=True)
        return Response(serializer.data)


class ReserveSeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, showtime_id: int):
        serializer = ReserveSeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        showtime = get_object_or_404(
            Showtime.objects.select_related('room'),
            pk=showtime_id,
        )
        seat = get_object_or_404(
            Seat,
            pk=serializer.validated_data['seat_id'],
            room=showtime.room,
        )
        if Ticket.objects.filter(showtime=showtime, seat=seat).exists():
            return Response(
                {'detail': 'This seat has already been purchased.'},
                status=status.HTTP_409_CONFLICT,
            )
        locked = acquire_seat_lock(showtime.id, seat.id, request.user.id)
        if not locked:
            owner = get_seat_lock_owner(showtime.id, seat.id)
            ttl = get_seat_lock_ttl(showtime.id, seat.id)
            return Response(
                {
                    'detail': 'This seat is temporarily reserved.',
                    'locked_by_me': owner == str(request.user.id),
                    'lock_ttl_seconds': ttl,
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            {
                'detail': 'Seat reserved successfully.',
                'showtime_id': showtime.id,
                'seat_id': seat.id,
                'lock_ttl_seconds': get_seat_lock_ttl(showtime.id, seat.id),
            },
            status=status.HTTP_200_OK,
        )
