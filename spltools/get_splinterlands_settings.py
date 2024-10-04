import json
import urllib
from .settings import *

def get_splinterlands_settings():
    """
    Retrieve Splinterlands settings
    
    Parameters
    ----------
        
    None
        
    Returns
    -------
        
    settings : dictionary with splinterlands settings
    """
    try:
        with urllib.request.urlopen(f"{BASE_URL}/settings") as request:
            settings = json.loads(request.read())
            return settings
    except urllib.error.URLError as e:
        print(f"Error {e}") 
