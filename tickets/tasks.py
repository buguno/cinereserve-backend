from celery import shared_task
from django.core.mail import send_mail

from tickets.models import Ticket


@shared_task
def send_ticket_confirmation_email(ticket_id: int) -> None:
    ticket = Ticket.objects.select_related(
        'user', 'showtime__movie', 'seat'
    ).get(pk=ticket_id)

    subject = 'Your CineReserve ticket confirmation'
    message = (
        f'Hello, {ticket.user.username}!\n\n'
        f'Your ticket has been confirmed.\n'
        f'Movie: {ticket.showtime.movie.title}\n'
        f'Seat: {ticket.seat}\n'
        f'Showtime: {ticket.showtime.start_time}\n'
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[ticket.user.email],
        fail_silently=False,
    )
