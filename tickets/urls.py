from django.urls import path

from tickets.api.views import TicketListCreateView

urlpatterns = [
    path('my-tickets/', TicketListCreateView.as_view(), name='my_tickets'),
]
