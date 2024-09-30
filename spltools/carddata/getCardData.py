import json
import urllib

def getCardData():
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
            carddata = json.loads(request.read())
            carddata = [x for x in carddata if x['id'] < 10000]
            return carddata
    except urllib.error.URLError as e:
        print(f"Error {e}") 
        
