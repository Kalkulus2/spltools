from spltools.settings import BASE_URL, request_session


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
    response = request_session.get(f"{BASE_URL}/settings")
    if response:
        settings = response.json()
        return settings
    else:
        print(f"Error code {response.status_code}")
