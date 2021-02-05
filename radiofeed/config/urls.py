from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views as sitemaps_views
from django.urls import include, path
from django.views.generic import TemplateView

from radiofeed.episodes.sitemaps import EpisodeSitemap
from radiofeed.podcasts.sitemaps import CategorySitemap, PodcastSitemap
from radiofeed.users.views import accept_cookies, delete_account, user_preferences

sitemaps = {
    "categories": CategorySitemap,
    "episodes": EpisodeSitemap,
    "podcasts": PodcastSitemap,
}


urlpatterns = [
    path("", include("radiofeed.podcasts.urls")),
    path("", include("radiofeed.episodes.urls")),
    path("account/preferences/", user_preferences, name="user_preferences"),
    path("account/~delete/", delete_account, name="delete_account"),
    path("account/", include("turbo_allauth.urls")),
    path("accept-cookies/", accept_cookies, name="accept_cookies"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
    path(settings.ADMIN_URL, admin.site.urls),
    path(
        "sitemap.xml",
        sitemaps_views.index,
        {"sitemaps": sitemaps, "sitemap_url_name": "sitemaps"},
    ),
    path(
        "sitemap-<section>.xml",
        sitemaps_views.sitemap,
        {"sitemaps": sitemaps},
        name="sitemaps",
    ),
]


if settings.DEBUG:

    if "silk" in settings.INSTALLED_APPS:
        urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

    # static views
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # allow preview/debugging of error views in development
    urlpatterns += [
        path("errors/400/", TemplateView.as_view(template_name="400.html")),
        path("errors/403/", TemplateView.as_view(template_name="403.html")),
        path("errors/404/", TemplateView.as_view(template_name="404.html")),
        path("errors/405/", TemplateView.as_view(template_name="405.html")),
        path("errors/500/", TemplateView.as_view(template_name="500.html")),
        path("errors/csrf/", TemplateView.as_view(template_name="403_csrf.html")),
    ]
