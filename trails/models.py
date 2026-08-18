from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.db.models import Sum, Count
from django.urls import reverse

TWO_PLACES = Decimal("0.01")


def _clean_miles(value):
    """SQLite's Sum() over a DecimalField round-trips through floating point,
    so aggregated totals can come back as e.g. Decimal('7.20000000000004').
    Quantize back to the field's real precision (2 decimal places)."""
    if value is None:
        return Decimal("0.00")
    return Decimal(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


class Hike(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MODERATE = "moderate", "Moderate"
        HARD = "hard", "Hard"
        STRENUOUS = "strenuous", "Strenuous"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hikes"
    )
    trail_name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True)
    date_hiked = models.DateField()
    distance_miles = models.DecimalField(max_digits=6, decimal_places=2)
    elevation_gain_ft = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    difficulty = models.CharField(
        max_length=10, choices=Difficulty.choices, default=Difficulty.MODERATE
    )
    rating = models.PositiveSmallIntegerField(default=3)  # 1-5
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_hiked", "-created_at"]

    def __str__(self):
        return f"{self.trail_name} ({self.date_hiked})"

    def get_absolute_url(self):
        return reverse("hike_detail", args=[self.pk])

    @property
    def stars_filled(self):
        return range(self.rating)

    @property
    def stars_empty(self):
        return range(5 - self.rating)

    @property
    def duration_display(self):
        if not self.duration_minutes:
            return None
        hours, minutes = divmod(self.duration_minutes, 60)
        if hours and minutes:
            return f"{hours}h {minutes}m"
        if hours:
            return f"{hours}h"
        return f"{minutes}m"


# Milestone thresholds, checked against lifetime totals. Kept as plain data
# (not a model) since badges are derived state, computed on read — there is
# nothing to keep in sync.
MILE_BADGES = [10, 25, 50, 100, 250, 500]
ELEVATION_BADGES = [5000, 10000, 25000, 50000, 100000]
HIKE_COUNT_BADGES = [5, 10, 25, 50, 100]


def user_stats(user):
    """Aggregate lifetime + this-year stats and earned badges for a user."""
    qs = Hike.objects.filter(owner=user)
    totals = qs.aggregate(
        total_miles=Sum("distance_miles"),
        total_elevation=Sum("elevation_gain_ft"),
        total_hikes=Count("id"),
    )
    total_miles = _clean_miles(totals["total_miles"])
    total_elevation = totals["total_elevation"] or 0
    total_hikes = totals["total_hikes"] or 0

    this_year = qs.filter(date_hiked__year=date.today().year)
    year_totals = this_year.aggregate(
        miles=Sum("distance_miles"), hikes=Count("id")
    )
    year_miles = _clean_miles(year_totals["miles"])

    badges = []
    for threshold in MILE_BADGES:
        if total_miles >= threshold:
            badges.append(f"{threshold} Miles")
    for threshold in ELEVATION_BADGES:
        if total_elevation >= threshold:
            badges.append(f"{threshold:,} ft Climbed")
    for threshold in HIKE_COUNT_BADGES:
        if total_hikes >= threshold:
            badges.append(f"{threshold} Hikes")

    return {
        "total_miles": total_miles,
        "total_elevation": total_elevation,
        "total_hikes": total_hikes,
        "year_miles": year_miles,
        "year_hikes": year_totals["hikes"] or 0,
        "badges": badges,
    }
