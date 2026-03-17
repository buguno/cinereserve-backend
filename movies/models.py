from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    release_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
