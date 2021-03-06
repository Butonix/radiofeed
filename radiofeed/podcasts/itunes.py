import dataclasses
import json
from typing import Dict, List, Optional, Tuple, Union

from django.core.cache import cache
from django.utils.encoding import force_str

import requests

from .models import Category, Podcast

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"


class Timeout(requests.exceptions.Timeout):
    pass


class Invalid(requests.RequestException):
    pass


@dataclasses.dataclass
class SearchResult:
    rss: str
    itunes: str
    title: str
    image: str
    podcast: Optional[Podcast] = None

    def as_dict(self) -> Dict:
        return {
            "rss": self.rss,
            "title": self.title,
            "itunes": self.itunes,
            "image": self.image,
            "podcast": self.podcast,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict())


SearchResultList = List[SearchResult]


def fetch_itunes_genre(
    genre_id: Union[str, int],
    num_results: int = 20,
) -> Tuple[SearchResultList, List[Podcast]]:
    """Fetch top rated results for genre"""
    return _get_or_create_podcasts(
        _get_search_results(
            {
                "term": "podcast",
                "limit": num_results,
                "genreId": genre_id,
            },
            cache_key=f"itunes:genre:{genre_id}",
        )
    )


def search_itunes(
    search_term: str, num_results: int = 12
) -> Tuple[SearchResultList, List[Podcast]]:
    """Does a search query on the iTunes API."""

    return _get_or_create_podcasts(
        _get_search_results(
            {
                "media": "podcast",
                "limit": num_results,
                "term": force_str(search_term),
            },
            cache_key=f"itunes:search:{search_term}",
        )
    )


def crawl_itunes(limit: int = 100) -> int:
    categories = (
        Category.objects.filter(itunes_genre_id__isnull=False)
        .prefetch_related("podcast_set")
        .order_by("name")
    )
    new_podcasts = 0

    for category in categories:
        podcasts: List[Podcast] = []

        try:
            results, podcasts = fetch_itunes_genre(
                category.itunes_genre_id, num_results=limit
            )
        except (Invalid, Timeout):
            continue

        new_podcasts += len(podcasts)
    return new_podcasts


def _get_or_create_podcasts(
    results: SearchResultList,
) -> Tuple[SearchResultList, List[Podcast]]:
    """Looks up podcast associated with result. Optionally adds new podcasts if not found"""
    podcasts = Podcast.objects.filter(itunes__in=[r.itunes for r in results]).in_bulk(
        field_name="itunes"
    )
    new_podcasts = []
    for result in results:
        result.podcast = podcasts.get(result.itunes, None)
        if result.podcast is None:
            new_podcasts.append(
                Podcast(title=result.title, rss=result.rss, itunes=result.itunes)
            )

    if new_podcasts:
        Podcast.objects.bulk_create(new_podcasts, ignore_conflicts=True)

    return results, new_podcasts


def _get_search_results(
    params: Dict,
    cache_key: str,
    cache_timeout: int = 86400,
    requests_timeout: int = 3,
) -> SearchResultList:

    results = cache.get(cache_key)
    if results is None:
        try:
            response = requests.get(
                ITUNES_SEARCH_URL,
                params,
                timeout=requests_timeout,
                verify=True,
            )
            response.raise_for_status()
            results = response.json()["results"]
            cache.set(cache_key, results, timeout=cache_timeout)
        except KeyError as e:
            raise Invalid from e
        except requests.exceptions.Timeout as e:
            raise Timeout from e
        except requests.RequestException as e:
            raise Invalid from e

    return [
        SearchResult(
            item["feedUrl"],
            item["trackViewUrl"],
            item["collectionName"],
            item["artworkUrl600"],
        )
        for item in results
        if "feedUrl" in item
    ]
