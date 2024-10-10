from enum import Enum

BASE_URL = "https://api2.splinterlands.com"

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
