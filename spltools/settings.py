import requests
from enum import Enum
from requests.adapters import HTTPAdapter, Retry

BASE_URL = "https://api2.splinterlands.com"
GUILD_URL = f"{BASE_URL}/guilds"
BATTLE_URL = f"{BASE_URL}/battle"
BATTLE_LINK_URL = "https://splinterlands.com/battle"
TOURNAMENT_URL = f"{BASE_URL}/tournaments"

set_str_to_int = {"alpha": 0, "beta": 1, "untamed": 4, "gladius": 6,
                  "chaos": 7, "rebellion": 12}           
edition_to_str = {0: "alpha", 1: "beta", 2: "promo", 3: "reward",
                  4: "untamed", 5: "dice", 6: "gladius", 7: "chaos",
                  8: "rift", 10: "soulbound", 12: "rebellion",
                  13: "soulboundrb"}


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
HIVE_IMG_URL = "https://images.hive.blog/"
PREFIX_30X30 = f"{HIVE_IMG_URL}/30x30"
CROWN_IMAGE = (f"{PREFIX_30X30}/{ARTWORK_URL}"
               + "/website/guilds/img_guild_crown_75.png")
MERITS_IMAGE = (f"{PREFIX_30X30}/{ARTWORK_URL}"
                + "/website/icons/img_merit_256.png")
SPS_IMAGE = (f"{PREFIX_30X30}/{ARTWORK_URL}"
             + "/website/ui_elements/shop/cl/img_sps-shard_128.png")


request_session = requests.Session()
retries = Retry(total=10,
                backoff_factor=2,
                status_forcelist=[429, 500, 502, 503, 504])
request_session.mount('http://', HTTPAdapter(max_retries=retries))
