from django.contrib import admin

from movies.models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'is_active')
    search_fields = ('title',)
