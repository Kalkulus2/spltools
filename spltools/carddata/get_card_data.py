import json
import urllib
from .. import settings

def get_card_data_raw():
    """
    Retrieve details of all Splinterlands cards.
    Discard any Soulkeep data.
    
    Parameters
    ----------
        
    None
        
    Returns
    -------
        
    card_data : List of cards, where each element is a dictionary 
        representing a card. 
    """
    try:
        url = f"{settings.BASE_URL}/cards/get_details"
        with urllib.request.urlopen(url) as request:
            card_data = json.loads(request.read())
            card_data = [x for x in card_data if x['id'] < 10001]
            return card_data
    except urllib.error.URLError as e:
        print(f"Error {e}") 
        
def get_card_data():
    """
    Retrieve details of all Splinterlands cards. Discard any Soulkeep 
    data. This function differs from get_card_data_raw in that it
    returns a dict of cards, where the keys are the card ids, and the 
    values are the entries in the list of cards returned by the 
    Splinterlands API.  
    
    Parameters
    ----------
    
    None
    
    Returns
    -------
    
    card_dict : Dict of cards, where each value is a dictionary
        representing a card. 
    """
    raw_data = get_card_data_raw()
    card_dict = {}
    for c in raw_data:
        card_dict[c['id']] = c
    return card_dict
