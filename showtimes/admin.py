from django.contrib import admin

from showtimes.models import Room, Seat, Showtime


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 10


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'row', 'number')
    list_filter = ('room',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    inlines = [SeatInline]


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'movie', 'room', 'start_time')
    list_filter = ('movie', 'room', 'start_time')
