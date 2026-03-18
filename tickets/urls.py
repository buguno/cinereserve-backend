from django.urls import path

from tickets.api.views import TicketCheckoutView, TicketListView

urlpatterns = [
    path('my-tickets/', TicketListView.as_view(), name='my_tickets'),
    path('checkout/', TicketCheckoutView.as_view(), name='ticket_checkout'),
]
