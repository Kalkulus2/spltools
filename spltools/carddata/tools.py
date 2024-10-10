from spltools.settings import set_str_to_int, Edition, Tier


def in_set(card_id, set_, card_data):
    """
    Checks if a card belongs to the given set.

    Parameters
    ----------

    card_id : int
        Integer id for the card

    set_ : str or int
        String or integer id for the set (case insensitive). Valid names
        are "alpha", "beta", "untamed", "gladius", "chaos", "rebellion",
        and valid integers are 0, 1, 4, 6, 7, and 12.

    card_data: dict
        Card data dictionary.

    Returns
    -------

    tf : bool
        True if the card is in the set, False otherwise.

    """
    if (isinstance(set_, str)):
        if (set_.lower() in set_str_to_int.keys()):
            set_ = set_str_to_int[set_.lower()]
        else:
            valid_set_strings = list(set_str_to_int.keys())
            raise ValueError(
                f"Valid set strings are {valid_set_strings}")
    else:
        if (set_ not in set_str_to_int.values()):
            valid_values = list(set_str_to_int.values())
            raise ValueError(f"Valid set values are {valid_values}")

    card_edition_str = card_data[card_id]['editions']
    if ("," in card_edition_str):  # Alpha/Beta core
        eds = [int(x) for x in card_edition_str.split(",")]
        if (set_ in eds):
            return True
        else:
            return False

    card_edition = int(card_edition_str)
    if (set_ == card_edition):
        return True
    else:
        tier = card_data[card_id]['tier']
        if (set_ == Edition.ALPHA.value):
            if (card_edition == Edition.PROMO.value):
                if (card_id <= 78):
                    return True
                else:
                    return False
        elif (set_ == Edition.BETA.value):
            if (card_edition == Edition.PROMO.value and tier is None
                    and card_id > 78):
                return True
            elif (card_edition == Edition.REWARDS.value and tier is None):
                return True
            else:
                return False
        elif (set_ == Edition.UNTAMED.value):
            if (card_edition == Edition.DICE.value):
                return True
            elif (card_edition == Edition.PROMO.value
                  and (tier in (Tier.UNTAMED.value, Tier.DICE.value))):
                return True
            elif (card_edition == Edition.REWARDS.value
                  and tier == Tier.DICE.value):
                return True
            else:
                return False
        elif (set_ == Edition.CHAOS.value):
            if (card_edition == Edition.RIFT.value):
                return True
            elif (card_edition in (Edition.PROMO.value, Edition.REWARDS.value)
                  and tier == Tier.CHAOS.value):
                return True
            elif (card_edition == Edition.SOULBOUND.value):
                return True
            else:
                return False
        elif (set_ == Edition.REBELLION.value):
            if (card_edition == Edition.PROMO.value
                    and tier == Tier.REBELLION.value):
                return True
            elif (card_edition == Edition.SOULBOUNDRB.value):
                return True
            else:
                return False
    return False
