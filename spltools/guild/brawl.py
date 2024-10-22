from spltools.settings import TOURNAMENT_URL, SPS_IMAGE, MERITS_IMAGE, \
    CROWN_IMAGE, request_session


class Brawl:
    """
    Class for working with brawl data. Contains more data for one guild
    than the rest, since the find_brawl api call includes a guild id
    specification.

    Parameters
    ----------
    GUILD_ID : str
        Unique string identifier of the specified guild.
    GUILD_NAME : str
        Name of the specified guild
    BRAWL_ID : str
        Unique brawl identifier.
    data : dict
        Dictionary returned by TOURNAMENT_URL/find_brawl.
    tier : int
        Brawl tier.
    player_data : list
        List of dictionaries containing individual player results.
    players : list
        Players in the specified guild that played in this brawl.
    player_results : list
        List of BrawlerResults instances for each player.
    guilds_data : list
        List of dictionaries containing each guilds results, names, ids
        etc.
    guild_names : list
        List of all guilds (names) that played in this brawl.
    guild_ids : list
        List of all guild (ids) that played in this brawl.
    opponents : list
        Like guild_names, but without GUILD_NAME
    opponents_ids : list
        Like guild_ids, but without GUILD_ID
    guild_wins, guild_losses, guild_autowins : dict
        Dictionaries of guild wins, losses and autowins, with guild
        names as keys.
    guild_crowns, guild_sps, guild_merits : dict
        Dictionaries of crown, sps and merits rewards, with guild
        names as keys.
    """
    def __init__(self, GUILD_ID, BRAWL_ID, brawl_data=None):
        self.GUILD_ID = GUILD_ID
        self.BRAWL_ID = BRAWL_ID
        self._get_brawl_data(brawl_data)
        self.tier = self.data['data']['challenge_level'] + 1
        self.player_data = self.data['players']
        self.players = [x['player'] for x in self.player_data]
        self.player_results = [BrawlerResults(x) for x in self.player_data]
        self.guilds_data = self.data['guilds']
        self.guild_ids = [x['id'] for x in self.guilds_data]
        self.guild_names = [x['name'] for x in self.guilds_data]
        self.guild_wins = {}
        self.guild_losses = {}
        self.guild_draws = {}
        self.guild_auto_wins = {}
        self.guild_crowns = {}
        self.guild_sps = {}
        self.guild_merits = {}
        for gd in self.guilds_data:
            gn = gd['name']
            self.guild_wins[gn] = gd['wins']
            self.guild_losses[gn] = gd['losses']
            self.guild_draws[gn] = gd['draws']
            if ('auto_wins' in gd.keys()):
                self.guild_auto_wins[gn] = gd['auto_wins']
            else:
                self.guild_auto_wins[gn] = 0
            self.guild_crowns[gn] = gd['total_payout']
            self.guild_sps[gn] = gd['member_sps_payout']
            self.guild_merits[gn] = gd['member_merits_payout']
        self.opponents = []
        self.opponents_ids = []
        for gid, gn in zip(self.guild_ids, self.guild_names):
            if (gid == GUILD_ID):
                self.GUILD_NAME = gn
            else:
                self.opponents.append(gn)
                self.opponents_ids.append(gid)

    def _get_brawl_data(self, brawl_data=None):
        if brawl_data is None:
            url = (f'{TOURNAMENT_URL}/find_brawl?id={self.BRAWL_ID}'
                   + f'&guild_id={self.GUILD_ID}')
            response = request_session.get(url)
            if response:
                self.data = response.json()
        else:
            self.data = brawl_data

    def __str__(self):
        strr = f"Brawl({self.GUILD_ID}, {self.BRAWL_ID})\n"
        strr += f"    Guild: {self.GUILD_NAME}\n"
        strr += f"    Tier: {self.tier}\n"
        strr += f"    Players: {self.players}\n"
        strr += f"    Opponents: {self.opponents}"
        return strr

    def print_results(self):
        """
        Print all results for this guild's players
        """
        for result in self.player_results:
            print(result)

    def markdown_results_and_payouts(self):
        """
        Print a markdown table of all the guild results in this brawl.
        """
        strr = f"Guild | Wins | Losses | Crowns {CROWN_IMAGE}"
        strr += f" | SPS {SPS_IMAGE} | Merits {MERITS_IMAGE}\n"
        strr += "--|--|--|--|--|--\n"
        for gn in self.guild_names:
            auto = (f"+{self.guild_auto_wins[gn]}" 
                    if self.guild_auto_wins[gn] > 0 else '')
            strr += f"{gn} | {self.guild_wins[gn]}{auto} | "
            strr += f"{self.guild_losses[gn]} | {self.guild_crowns[gn]} | "
            strr += f"{self.guild_sps[gn]} | {self.guild_merits[gn]}\n"
        return strr
    

class BrawlerResults:
    """
    Simple container for a player's results in a specific brawl

    Attributes
    ----------
    player : str
        Player name.
    wins : int
        Number of wins.
    losses: int
        Number of losses.
    auto_wins : int
        Number of auto-wins.
    total_battles : int
        Number of battles.
    entered_battles : int
        Number of battles entered.
    fray_index : int
        The fray the player was in.
    """
    def __init__(self, data):
        """
        Parameters
        ----------
        data : dict
            Data describing the player's results. Neccesary data
            entries are player, wins, losses, auto_wins, total_battles,
            entered_battles and fray_index.
        """
        self.player = data['player']
        self.wins = data['wins']
        self.losses = data['losses']
        if ('auto_wins' in data.keys()):
            self.auto_wins = data['auto_wins']
        else:
            self.auto_wins = 0
        self.total_battles = data['total_battles']
        self.entered_battles = data['entered_battles']
        self.fray_index = data['fray_index']

    def __str__(self):
        strr = f"{self.player}, fray {self.fray_index}: {self.wins} W, "
        strr += f"{self.losses} L, {self.auto_wins} AW."
        return strr
