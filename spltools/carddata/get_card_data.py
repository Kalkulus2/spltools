from spltools.settings import BASE_URL, request_session


def get_card_data_raw():
    """
    Retrieve details of all Splinterlands cards.
    Discard any Soulkeep data.

    Parameters
    ----------

    None

    Returns
    -------

    card_data : list
        List of cards, where each element is a dictionary representing
        a card.
    """
    url = f"{BASE_URL}/cards/get_details"
    response = request_session.get(url)
    if response:
        card_data = response.json()
        card_data = [x for x in card_data if x['id'] < 10001]
        return card_data
    else:
        print(f"Error code {response.status_code}")


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

    card_dict : dict
        Dictionary of cards with lookup by id, where each value is
        another dictionary representing a card.
    """
    raw_data = get_card_data_raw()
    if raw_data is not None:
        card_dict = {}
        for c in raw_data:
            card_dict[c['id']] = c
        return card_dict
    else:
        print("Error in get_card_data_raw()")
