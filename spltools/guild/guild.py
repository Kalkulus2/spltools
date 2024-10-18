import requests
from spltools.settings import GUILD_URL


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
            the unique string identifier for the guild
        """
        success = True
        try:
            response = requests.get(f"{GUILD_URL}/find?id={id}")
        except Exception as E:
            success = False
            print("Error while downloading guild data:", E)

        try:
            data = response.json()
        except Exception as E:
            success = False
            print("Error while parsing json:", E)

        if (not success):
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
        if (self.members is None):
            success = True
            try:
                response = requests.get(
                    f"{GUILD_URL}/members?guild_id={self.id}")
            except Exception as E:
                success = False
                print("Error while downloading guild member data:", E)

            try:
                data = response.json()
            except Exception as E:
                success = False
                print("Error while parsing json:", E)
            if (not success):
                return []
            self.members = [p['player'] for p in data]
            return self.members
        else:
            return self.members
