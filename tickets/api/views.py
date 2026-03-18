from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from showtimes.models import Seat, Showtime
from tickets.api.serializers import CheckoutSerializer, TicketSerializer
from tickets.models import Ticket
from tickets.services import CheckoutError, checkout_ticket


class TicketListView(ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Ticket.objects
            .filter(user=self.request.user)
            .select_related('showtime__movie', 'showtime__room', 'seat')
            .order_by('-purchased_at')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        showtime = get_object_or_404(
            Showtime.objects.select_related('room'),
            pk=serializer.validated_data['showtime_id'],
        )

        if showtime.start_time <= timezone.now():
            return Response(
                {'detail': 'You cannot buy tickets for past showtimes.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        seat = get_object_or_404(
            Seat,
            pk=serializer.validated_data['seat_id'],
            room=showtime.room,
        )

        try:
            ticket = checkout_ticket(
                showtime=showtime,
                seat=seat,
                user=request.user,
            )
        except CheckoutError as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            TicketSerializer(ticket).data,
            status=status.HTTP_201_CREATED,
        )
