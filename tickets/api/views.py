from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from tickets.api.serializers import TicketSerializer
from tickets.models import Ticket


class TicketListCreateView(ListCreateAPIView):
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
