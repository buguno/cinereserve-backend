from django.conf import settings
from django.db import models

from showtimes.models import Seat, Showtime


class Ticket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
    )
    showtime = models.ForeignKey(
        Showtime, on_delete=models.CASCADE, related_name='tickets'
    )
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('showtime', 'seat')

    def __str__(self):
        return f'Ticket: {self.user.username} - {self.showtime.movie.title} ({self.seat})'
