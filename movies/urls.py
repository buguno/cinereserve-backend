from django.urls import path

from movies.api.views import MovieListView

urlpatterns = [
    path('', MovieListView.as_view(), name='list_movies'),
]
