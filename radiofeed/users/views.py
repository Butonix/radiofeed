import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from turbo_response import TurboStream, redirect_303, render_form_response

from radiofeed.episodes.models import AudioLog, Favorite
from radiofeed.podcasts.models import Podcast, Subscription
from radiofeed.shortcuts import handle_form

from .forms import UserPreferencesForm


@login_required
def user_preferences(request: HttpRequest) -> HttpResponse:
    if result := handle_form(request, UserPreferencesForm, instance=request.user):

        result.form.save()
        messages.success(request, "Your preferences have been saved")
        return redirect_303(request.path)

    return render_form_response(request, result.form, "account/preferences.html")


@login_required
def user_stats(request: HttpRequest) -> HttpResponse:

    logs = AudioLog.objects.filter(user=request.user)
    subscriptions = Subscription.objects.filter(user=request.user)
    favorites = Favorite.objects.filter(user=request.user)

    most_listened = (
        Podcast.objects.filter(episode__audiolog__user=request.user)
        .annotate(num_listened=Count("episode__audiolog"))
        .order_by("-num_listened")
        .distinct()[:5]
    )

    return TemplateResponse(
        request,
        "account/stats.html",
        {
            "stats": {
                "listened": logs.count(),
                "in_progress": logs.filter(completed__isnull=True).count(),
                "completed": logs.filter(completed__isnull=False).count(),
                "subscriptions": subscriptions.count(),
                "favorites": favorites.count(),
            },
            "most_listened": most_listened,
        },
    )


@login_required
def delete_account(request: HttpRequest) -> HttpResponse:
    if request.method == "POST" and "confirm-delete" in request.POST:
        request.user.delete()
        logout(request)
        messages.info(request, "Your account has been deleted")
        return redirect_303(settings.HOME_URL)
    return TemplateResponse(request, "account/delete_account.html")


@require_POST
def accept_cookies(request: HttpRequest) -> HttpResponse:
    response = TurboStream("accept-cookies").remove.response()
    response.set_cookie(
        "accept-cookies",
        value="true",
        expires=timezone.now() + datetime.timedelta(days=30),
        samesite="Lax",
    )
    return response


@require_POST
def toggle_dark_mode(request: HttpRequest) -> HttpResponse:
    dark_mode = request.COOKIES.get("dark-mode")

    redirect_url = request.POST.get("redirect_url")
    if not redirect_url or not url_has_allowed_host_and_scheme(
        redirect_url, {request.get_host()}, request.is_secure()
    ):
        redirect_url = settings.HOME_URL

    response = redirect(redirect_url)

    if dark_mode:
        response.delete_cookie("dark-mode")
    else:
        response.set_cookie(
            "dark-mode",
            value="true",
            expires=timezone.now() + datetime.timedelta(days=30),
            samesite="Lax",
        )
    return response
