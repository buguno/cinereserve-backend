from django.contrib import admin

from tickets.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_movie', 'get_seat', 'purchased_at')

    list_filter = ('showtime__movie', 'purchased_at', 'user')

    search_fields = ('user__username', 'showtime__movie__title')

    def get_movie(self, obj):
        return obj.showtime.movie.title

    get_movie.short_description = 'Movie'

    def get_seat(self, obj):
        return f'{obj.seat.row}{obj.seat.number} ({obj.seat.room.name})'

    get_seat.short_description = 'Seat'
