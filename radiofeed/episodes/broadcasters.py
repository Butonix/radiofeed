# Third Party Libraries
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def player_stop(request, episode):
    player_message(request, "player.stop", {"episode": episode.id})


def player_start(request, episode):
    player_message(request, "player.start", {"episode": episode.id})


def player_timeupdate(request, episode, current_time, completed):
    player_message(
        request,
        "player.timeupdate",
        {
            "episode": episode.id,
            "info": {
                "duration": episode.get_duration_in_seconds(),
                "current_time": current_time,
                "completed": completed,
            },
        },
    )


def player_message(request, msg_type, data=None):
    data = {
        "type": msg_type,
        "request_id": request.session.session_key,
        **(data or {}),
    }
    async_to_sync(get_channel_layer().group_send)("player", data)