from .. import settings

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
        if (set_.lower() in settings.set_str_to_int.keys()):
            set_ = settings.set_str_to_int[set_.lower()]
        else:
            valid_set_strings = list(settings.set_str_to_int.keys())
            raise ValueError(
                f"Valid set strings are {valid_set_strings}")
    else:
        if (not set_ in settings.set_str_to_int.values()):
            valid_values = list(settings.set_str_to_int.values())
            raise ValueError(f"Valid set values are {valid_values}")
                
    card_edition_str = card_data[card_id]['editions']
    if ("," in card_edition_str): # Alpha/Beta core
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
        if (set_ == 0):
            if (card_edition==2): # Alpha promo
                if (card_id <= 78):
                    return True
                else:
                    return False
        elif (set_ == 1):
            if (card_edition == 2 and tier is None #Beta promo  
                and card_id > 78): 
                return True
            elif (card_edition == 3 and tier is None): # Beta rewards
                return True
            else:
                return False
        elif (set_ == 4):
            if (card_edition == 5):
                return True
            elif (card_edition == 2 and (tier in (3,4))): # Untamed promo
                return True
            elif (card_edition == 3 and tier == 4): # Untamed rewards
                return True
            else:
                return False
        elif (set_ == 7):
            if (card_edition == 8): # Riftwatchers
                return True
            elif (card_edition in (2,3) and tier == 7): # Chaos promo/rewards
                return True
            elif (card_edition == 10): # Chaos soulbounds
                return True
            else:
                return False
        elif (set_ == 12):
            if (card_edition == 2 and tier == 12): # Rebellion promos
                return True
            elif (card_edition == 13): # Rebellion rewards
                return True
            else:
                return False
    return False
