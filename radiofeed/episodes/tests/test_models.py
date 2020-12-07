# Third Party Libraries
import pytest

# Local
from ..factories import BookmarkFactory, EpisodeFactory
from ..models import Bookmark, Episode

pytestmark = pytest.mark.django_db


class TestEpisodeManager:
    def test_search(self):
        EpisodeFactory(title="testing")
        assert Episode.objects.search("testing").count() == 1


class TestEpisodeModel:
    def test_slug(self):
        episode = Episode(title="Testing")
        assert episode.slug == "testing"

    def test_slug_if_title_empty(self):
        assert Episode().slug == "episode"


class TestBookmarkManager:
    def test_search(self):
        episode = EpisodeFactory(title="testing")
        BookmarkFactory(episode=episode)
        assert Bookmark.objects.search("testing").count() == 1
