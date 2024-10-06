import json
import urllib
from spltools.settings import BASE_URL

def get_splinterlands_settings():
    """
    Retrieve Splinterlands settings
    
    Parameters
    ----------
        
    None
        
    Returns
    -------
        
    settings : dict
        Dictionary with Splinterlands settings
    """
    try:
        with urllib.request.urlopen(f"{BASE_URL}/settings") as request:
            settings = json.loads(request.read())
            return settings
    except urllib.error.URLError as e:
        print(f"Error {e}") 
