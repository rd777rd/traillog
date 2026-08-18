from django.contrib import admin

from .models import Hike


@admin.register(Hike)
class HikeAdmin(admin.ModelAdmin):
    list_display = (
        "trail_name",
        "owner",
        "date_hiked",
        "distance_miles",
        "elevation_gain_ft",
        "difficulty",
    )
    list_filter = ("difficulty", "date_hiked")
    search_fields = ("trail_name", "location", "owner__username")
