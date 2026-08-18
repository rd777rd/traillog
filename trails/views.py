from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import SignUpForm, HikeForm
from .models import Hike, user_stats


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "trails/landing.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to TrailLog, {user.username}.")
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "trails/signup.html", {"form": form})


@login_required
def dashboard(request):
    stats = user_stats(request.user)
    recent_hikes = Hike.objects.filter(owner=request.user)[:5]
    return render(
        request,
        "trails/dashboard.html",
        {"stats": stats, "recent_hikes": recent_hikes},
    )


@login_required
def hike_list(request):
    qs = Hike.objects.filter(owner=request.user)

    difficulty = request.GET.get("difficulty", "")
    if difficulty in dict(Hike.Difficulty.choices):
        qs = qs.filter(difficulty=difficulty)

    year = request.GET.get("year", "")
    if year.isdigit():
        qs = qs.filter(date_hiked__year=int(year))

    query = request.GET.get("q", "").strip()
    if query:
        qs = qs.filter(trail_name__icontains=query)

    years = sorted(
        {
            d.year
            for d in Hike.objects.filter(owner=request.user).values_list(
                "date_hiked", flat=True
            )
        },
        reverse=True,
    )

    return render(
        request,
        "trails/hike_list.html",
        {
            "hikes": qs,
            "years": years,
            "selected_difficulty": difficulty,
            "selected_year": year,
            "query": query,
            "difficulties": Hike.Difficulty.choices,
        },
    )


@login_required
def hike_detail(request, pk):
    hike = get_object_or_404(Hike, pk=pk, owner=request.user)
    return render(request, "trails/hike_detail.html", {"hike": hike})


@login_required
def hike_add(request):
    if request.method == "POST":
        form = HikeForm(request.POST)
        if form.is_valid():
            hike = form.save(commit=False)
            hike.owner = request.user
            hike.save()
            messages.success(request, f"Logged {hike.trail_name}.")
            return redirect("hike_detail", pk=hike.pk)
    else:
        form = HikeForm()
    return render(request, "trails/hike_form.html", {"form": form, "is_edit": False})


@login_required
def hike_edit(request, pk):
    hike = get_object_or_404(Hike, pk=pk, owner=request.user)
    if request.method == "POST":
        form = HikeForm(request.POST, instance=hike)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {hike.trail_name}.")
            return redirect("hike_detail", pk=hike.pk)
    else:
        form = HikeForm(instance=hike)
    return render(
        request, "trails/hike_form.html", {"form": form, "is_edit": True, "hike": hike}
    )


@login_required
@require_POST
def hike_delete(request, pk):
    hike = get_object_or_404(Hike, pk=pk, owner=request.user)
    name = hike.trail_name
    hike.delete()
    messages.success(request, f"Deleted {name}.")
    return redirect("hike_list")
