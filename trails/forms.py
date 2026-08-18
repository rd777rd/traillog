from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Hike


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class HikeForm(forms.ModelForm):
    class Meta:
        model = Hike
        fields = [
            "trail_name",
            "location",
            "date_hiked",
            "distance_miles",
            "elevation_gain_ft",
            "duration_minutes",
            "difficulty",
            "rating",
            "notes",
        ]
        widgets = {
            "date_hiked": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "rating": forms.Select(choices=[(i, "★" * i) for i in range(1, 6)]),
        }
