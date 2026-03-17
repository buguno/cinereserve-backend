from django.db import models

from movies.models import Movie


class Room(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Seat(models.Model):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='seats'
    )
    row = models.CharField(max_length=2)
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('room', 'row', 'number')

    def __str__(self):
        return f'{self.room.name} - {self.row}{self.number}'


class Showtime(models.Model):
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='showtimes'
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='showtimes'
    )
    start_time = models.DateTimeField()

    def __str__(self):
        return f'{self.movie.title} | {self.room.name} @ {self.start_time.strftime("%d/%m %H:%M")}'
