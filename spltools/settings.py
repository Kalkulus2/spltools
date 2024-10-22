import requests
from enum import Enum
from requests.adapters import HTTPAdapter, Retry

BASE_URL = "https://api2.splinterlands.com"
GUILD_URL = f"{BASE_URL}/guilds"
TOURNAMENT_URL = f"{BASE_URL}/tournaments"

set_str_to_int = {
    "alpha": 0, "beta": 1, "untamed": 4, "gladius": 6, "chaos": 7,
    "rebellion": 12}           


class Edition(Enum):
    ALPHA = 0
    BETA = 1
    PROMO = 2
    REWARDS = 3
    UNTAMED = 4
    DICE = 5
    GLADIUS = 6
    CHAOS = 7
    RIFT = 8
    SOULBOUND = 10
    REBELLION = 12
    SOULBOUNDRB = 13


class Tier(Enum):
    UNTAMED = 3
    DICE = 4
    CHAOS = 7
    REBELLION = 12


ARTWORK_URL = "https://d36mxiodymuqjm.cloudfront.net"
PREFIX_30X30 = "https://images.hive.blog/30x30"
CROWN_IMAGE = (f"{PREFIX_30X30}/{ARTWORK_URL}"
               + "/website/guilds/img_guild_crown_75.png")
MERITS_IMAGE = (f"{PREFIX_30X30}/{ARTWORK_URL}"
                + "/website/icons/img_merit_256.png")
SPS_IMAGE = (f"{PREFIX_30X30}/{ARTWORK_URL}"
             + "/website/ui_elements/shop/cl/img_sps-shard_128.png")


request_session = requests.Session()
retries = Retry(total=5,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504])
request_session.mount('http://', HTTPAdapter(max_retries=retries))
