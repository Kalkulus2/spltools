from spltools.settings import BASE_URL, GUILD_URL, request_session


class Guild:
    """Class for holding guild data

    Attributes
    ----------
    id : str
        a unique string identifier for the guild
    name : str
        the name of the guild
    motto : str
        the motto of the guild
    numMembers : int
        the number of members in the guild
    members : list
        a list of the members in the guild
    rating : int
        the rating of the guild
    rank : int
        the rank of the guild

    """

    def __init__(self, id="d14d94bfab9f2532e26c33732cdba602d316f5bf"):
        """Initialize the class from the unique guild identifier

        Parameters
        ----------
        id : str
            The unique string identifier for the guild
        """
        response = request_session.get(f"{GUILD_URL}/find?id={id}")
        if response:
            data = response.json()
        else:
            print("Error status code: ", response.status_code)
            return

        # Setup guild class:
        self.id = id
        self.name = data['name']
        self.motto = data['motto']
        self.numMembers = data['num_members']
        self.members = None
        self.rating = int(data['rating'])
        self.rank = int(data['rank'])
        self._getMembers()

    def _getMembers(self):
        """Get guild member data
        """
        if self.members is None:
            url = f"{GUILD_URL}/members?guild_id={self.id}"
            response = request_session.get(url)
            if response:
                data = response.json()
            else:
                print("Error status code: ", response.status_code)
                return []
            self.members = [p['player'] for p in data
                            if p['status'] == "active"]
            return self.members
        return self.members

    def get_brawl_records(self):
        url = f"{GUILD_URL}/brawl_records?guild_id={self.id}"
        response = request_session.get(url)
        if response:
            data = response.json()['results']
            return data
        else:
            print("Error status code: ", response.status_code)
            return None

    def __str__(self):
        strr = f"{self.name}, Rank: {self.rank}, Members: {len(self.members)}"
        return strr


def get_guild_list():
    url = f"{GUILD_URL}/list"
    response = request_session.get(url)
    if response:
        data = response.json()['guilds']
        return data
    else:
        print("Error status code: ", response.status_code)
        return None


def get_player_guild(player):
    url = f"{BASE_URL}/players/details?name={player}"
    response = request_session.get(url)
    if response:
        data = response.json()
        if data['guild'] is None:
            return "-"
        return data['guild']['name']
    else:
        print("Error status code: ", response.status_code)
        return None
