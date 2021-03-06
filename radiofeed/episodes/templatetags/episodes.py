from typing import Dict, Optional, Union

from django import template

from .. import utils
from ..models import Episode
from ..player import PlayerInfo

register = template.Library()


@register.simple_tag(takes_context=True)
def is_playing(context: Dict, episode: Episode) -> bool:
    return context["request"].player.is_playing(episode)


@register.simple_tag(takes_context=True)
def get_player(context: Dict) -> PlayerInfo:
    return context["request"].player.as_dict()


@register.filter
def format_duration(total_seconds: Optional[int]) -> Union[str, int]:
    try:
        return utils.format_duration(int(total_seconds or 0))
    except ValueError:
        return 0
