from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Hike, user_stats


class SignupLoginTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        resp = self.client.post(
            reverse("signup"),
            {
                "username": "hiker1",
                "password1": "trailblazer42",
                "password2": "trailblazer42",
            },
        )
        self.assertEqual(User.objects.filter(username="hiker1").count(), 1)
        self.assertRedirects(resp, reverse("dashboard"))

    def test_login_required_redirects_dashboard(self):
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login"), resp.url)

    def test_landing_redirects_authenticated_user_to_dashboard(self):
        User.objects.create_user("hiker2", password="trailblazer42")
        self.client.login(username="hiker2", password="trailblazer42")
        resp = self.client.get(reverse("landing"))
        self.assertRedirects(resp, reverse("dashboard"))


class HikeCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("hiker", password="trailblazer42")
        self.other = User.objects.create_user("other", password="trailblazer42")
        self.client.login(username="hiker", password="trailblazer42")

    def test_add_hike(self):
        resp = self.client.post(
            reverse("hike_add"),
            {
                "trail_name": "Eagle Ridge Loop",
                "location": "Cascade Range",
                "date_hiked": "2026-06-01",
                "distance_miles": "8.4",
                "elevation_gain_ft": "2100",
                "duration_minutes": "240",
                "difficulty": "hard",
                "rating": "5",
                "notes": "Great views at the summit.",
            },
        )
        self.assertEqual(Hike.objects.count(), 1)
        hike = Hike.objects.first()
        self.assertEqual(hike.owner, self.user)
        self.assertRedirects(resp, reverse("hike_detail", args=[hike.pk]))

    def test_hike_list_only_shows_owner_hikes(self):
        Hike.objects.create(
            owner=self.user,
            trail_name="Mine",
            date_hiked=date(2026, 1, 1),
            distance_miles="3.0",
            elevation_gain_ft=500,
        )
        Hike.objects.create(
            owner=self.other,
            trail_name="Theirs",
            date_hiked=date(2026, 1, 1),
            distance_miles="3.0",
            elevation_gain_ft=500,
        )
        resp = self.client.get(reverse("hike_list"))
        names = [h.trail_name for h in resp.context["hikes"]]
        self.assertEqual(names, ["Mine"])

    def test_other_users_hike_detail_is_404_not_403(self):
        hike = Hike.objects.create(
            owner=self.other,
            trail_name="Theirs",
            date_hiked=date(2026, 1, 1),
            distance_miles="3.0",
            elevation_gain_ft=500,
        )
        resp = self.client.get(reverse("hike_detail", args=[hike.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_cannot_edit_other_users_hike(self):
        hike = Hike.objects.create(
            owner=self.other,
            trail_name="Theirs",
            date_hiked=date(2026, 1, 1),
            distance_miles="3.0",
            elevation_gain_ft=500,
        )
        resp = self.client.get(reverse("hike_edit", args=[hike.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_cannot_delete_other_users_hike(self):
        hike = Hike.objects.create(
            owner=self.other,
            trail_name="Theirs",
            date_hiked=date(2026, 1, 1),
            distance_miles="3.0",
            elevation_gain_ft=500,
        )
        resp = self.client.post(reverse("hike_delete", args=[hike.pk]))
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Hike.objects.filter(pk=hike.pk).exists())

    def test_delete_own_hike(self):
        hike = Hike.objects.create(
            owner=self.user,
            trail_name="Mine",
            date_hiked=date(2026, 1, 1),
            distance_miles="3.0",
            elevation_gain_ft=500,
        )
        resp = self.client.post(reverse("hike_delete", args=[hike.pk]))
        self.assertRedirects(resp, reverse("hike_list"))
        self.assertFalse(Hike.objects.filter(pk=hike.pk).exists())

    def test_edit_own_hike(self):
        hike = Hike.objects.create(
            owner=self.user,
            trail_name="Old Name",
            date_hiked=date(2026, 1, 1),
            distance_miles="3.0",
            elevation_gain_ft=500,
        )
        resp = self.client.post(
            reverse("hike_edit", args=[hike.pk]),
            {
                "trail_name": "New Name",
                "location": "",
                "date_hiked": "2026-01-01",
                "distance_miles": "3.0",
                "elevation_gain_ft": "500",
                "difficulty": "easy",
                "rating": "3",
                "notes": "",
            },
        )
        hike.refresh_from_db()
        self.assertEqual(hike.trail_name, "New Name")
        self.assertRedirects(resp, reverse("hike_detail", args=[hike.pk]))

    def test_filter_by_difficulty(self):
        Hike.objects.create(
            owner=self.user, trail_name="Easy One", date_hiked=date(2026, 1, 1),
            distance_miles="2.0", elevation_gain_ft=200, difficulty="easy",
        )
        Hike.objects.create(
            owner=self.user, trail_name="Hard One", date_hiked=date(2026, 1, 1),
            distance_miles="9.0", elevation_gain_ft=3000, difficulty="hard",
        )
        resp = self.client.get(reverse("hike_list"), {"difficulty": "hard"})
        names = [h.trail_name for h in resp.context["hikes"]]
        self.assertEqual(names, ["Hard One"])


class StatsAndBadgeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("hiker", password="trailblazer42")

    def test_empty_stats(self):
        stats = user_stats(self.user)
        self.assertEqual(stats["total_miles"], 0)
        self.assertEqual(stats["total_hikes"], 0)
        self.assertEqual(stats["badges"], [])

    def test_aggregate_totals_and_badges(self):
        Hike.objects.create(
            owner=self.user, trail_name="A", date_hiked=date(2026, 1, 1),
            distance_miles="6.0", elevation_gain_ft=3000,
        )
        Hike.objects.create(
            owner=self.user, trail_name="B", date_hiked=date(2026, 2, 1),
            distance_miles="5.0", elevation_gain_ft=2500,
        )
        stats = user_stats(self.user)
        self.assertEqual(stats["total_miles"], 11)
        self.assertEqual(stats["total_elevation"], 5500)
        self.assertEqual(stats["total_hikes"], 2)
        self.assertIn("10 Miles", stats["badges"])
        self.assertIn("5,000 ft Climbed", stats["badges"])
        self.assertNotIn("25 Miles", stats["badges"])

    def test_stats_are_per_user_isolated(self):
        other = User.objects.create_user("other", password="trailblazer42")
        Hike.objects.create(
            owner=other, trail_name="Not mine", date_hiked=date(2026, 1, 1),
            distance_miles="100.0", elevation_gain_ft=50000,
        )
        stats = user_stats(self.user)
        self.assertEqual(stats["total_miles"], 0)
        self.assertEqual(stats["total_hikes"], 0)

    def test_year_scoped_stats(self):
        Hike.objects.create(
            owner=self.user, trail_name="This year", date_hiked=date.today(),
            distance_miles="4.0", elevation_gain_ft=1000,
        )
        Hike.objects.create(
            owner=self.user, trail_name="Old", date_hiked=date(2020, 1, 1),
            distance_miles="4.0", elevation_gain_ft=1000,
        )
        stats = user_stats(self.user)
        self.assertEqual(stats["year_miles"], 4)
        self.assertEqual(stats["year_hikes"], 1)
