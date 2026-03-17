from django.urls import path

from showtimes.api.views import ShowtimeListView

urlpatterns = [
    path('', ShowtimeListView.as_view(), name='list_showtimes'),
]
