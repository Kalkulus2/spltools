import json
import urllib

def get_card_data():
    """
    Retrieve details of all Splinterlands cards.
    Discard any Soulkeep data.
    
    Parameters
    ----------
        
    None
        
    Returns
    -------
        
    carddata : List of cards, where each element is a dictionary representing a card. 
    """
    try:
        with urllib.request.urlopen("https://api2.splinterlands.com/cards/get_details") as request:
            card_data = json.loads(request.read())
            card_data = [x for x in card_data if x['id'] < 10001]
            return card_data
    except urllib.error.URLError as e:
        print(f"Error {e}") 
        
