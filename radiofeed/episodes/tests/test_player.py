import pytest

from ..player import Player

pytestmark = pytest.mark.django_db


class TestPlayer:
    def test_empty(self, rf):
        req = rf.get("/")
        req.session = {}
        player = Player(req)
        assert not player
        assert player.get_episode() is None
        assert player.current_time == 0
        assert player.playback_rate == 1.0

    def test_not_empty(self, rf, episode):
        req = rf.get("/")
        req.session = {
            "player": {
                "episode": episode.id,
                "current_time": 1000,
                "playback_rate": 1.2,
            }
        }
        player = Player(req)
        assert player
        assert player.get_episode() == episode
        assert player.current_time == 1000
        assert player.playback_rate == 1.2

    def test_eject(self, rf, episode):
        req = rf.get("/")
        req.session = {
            "player": {
                "episode": episode.id,
                "current_time": 1000,
                "playback_rate": 1.2,
            }
        }

        player = Player(req)
        assert player.current_time == 1000
        assert player.playback_rate == 1.2
        current_episode = player.eject()

        assert current_episode == episode

        assert not player
        assert player.current_time == 0
        assert player.playback_rate == 1.0

    def test_is_playing_true(self, rf, episode):
        req = rf.get("/")
        req.session = {
            "player": {
                "episode": episode.id,
                "current_time": 1000,
                "playback_rate": 1.2,
            }
        }
        player = Player(req)
        assert player.is_playing(episode)

    def test_is_playing_false(self, rf, episode):
        req = rf.get("/")
        req.session = {
            "player": {"episode": 12345, "current_time": 1000, "playback_rate": 1.2}
        }
        player = Player(req)
        assert not player.is_playing(episode)

    def test_is_playing_empty(self, rf, episode):
        req = rf.get("/")
        req.session = {}
        player = Player(req)
        assert not player.is_playing(episode)
