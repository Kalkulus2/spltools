import os
import sys
import json
import numpy as np
import time
sys.path.insert(0, os.path.abspath('..'))
from spltools.guild import Guild, get_guild_list, get_player_guild, Brawl
from spltools.settings import request_session, TOURNAMENT_URL

stop_at_rank = 300
guild_list = get_guild_list()
guild_list = guild_list[:stop_at_rank]

data_dir = "../data/brawl_data"


def download_brawl_data(GUILD_ID, BRAWL_ID):
    """
    Download brawl data if it is not already present in data_dir.

    Parameters
    ----------

    GUILD_ID : str
        Unique guild identifier
    BRAWL_ID : str
        Unique brawl identifier
    """
    filepath = f"{data_dir}/{GUILD_ID}_{BRAWL_ID}"
    if os.path.isfile(filepath):
        return
    else:
        url = (f"{TOURNAMENT_URL}/find_brawl?"
               + f"id={BRAWL_ID}&guild_id={GUILD_ID}")
        response = request_session.get(url)
        if response:
            with open(filepath, "w") as f:
                f.write(response.text)
        time.sleep(1)


def load_brawl_data(GUILD_ID, BRAWL_ID):
    """
    Load brawl data from file in data_dir

    Parameters
    ----------

    GUILD_ID : str
        Unique guild identifier
    BRAWL_ID : str
        Unique brawl identifier
    """
    filepath = f"{data_dir}/{GUILD_ID}_{BRAWL_ID}"
    if os.path.isfile(filepath):
        with open(filepath, "r") as iF:
            return json.loads(iF.read())


class BrawlHistory:
    """
    Class for storing brawl history data. Contains methods to store
    brawl data and process it to extract the best brawlers.
    """
    def __init__(self, tier):
        self.tier = tier
        n_frays = {3: 18, 4: 21, 5: 25}
        duplicate_frays = {3: {4: 3, 8: 7},
                           4: {2: 1, 4: 3, 7: 6, 9: 8, 12: 11, 14: 13},
                           5: {4: 3, 8: 7, 10: 9, 11: 9, 15: 14, 16: 14}}
        self.n_frays = n_frays[tier]
        self.duplicate_frays = duplicate_frays[tier]
        self.unique_frays = list(range(1, self.n_frays + 1))
        for duplicate in self.duplicate_frays.keys():
            self.unique_frays.remove(duplicate)
        self.unique_fray_names = {}
        for f in self.unique_frays:
            self.unique_fray_names[f] = f"{f}"
        for k, v in self.duplicate_frays.items():
            self.unique_fray_names[v] += f"+{k}"
        self.fray_data = {}
        for i in self.unique_frays:
            self.fray_data[i] = {}

    def add_data(self, brawl_data):
        """
        Take a Brawl object and store the relevant data
        """
        if (brawl_data.tier != self.tier):
            return
        for pr in brawl_data.player_results:
            p = pr.player
            f = pr.fray_index+1
            if f in self.duplicate_frays.keys():
                f = self.duplicate_frays[f]
            d = {"wins": pr.wins, "losses": pr.losses, "count": 1,
                 "wr": pr.wins/max(1, pr.wins+pr.losses)}
            if (p in self.fray_data[f].keys()):
                for key, value in d.items():
                    self.fray_data[f][p][key] += value
            else:
                self.fray_data[f][p] = d

    def _fray_to_arrays(self, fray):
        """
        Convenience function for create numpy array of wins, losses and
        winrates from the stored dictionaries.
        """
        fd = self.fray_data[fray]
        players = np.array(list(fd.keys()))
        wins = np.array([x['wins'] for x in fd.values()])
        losses = np.array([x['losses'] for x in fd.values()])
        battles = wins+losses
        wrs = wins/battles
        return players, wins, losses, wrs

    def print_best_in_frays(self):
        """
        Print a markdowntable with the best brawlers in each fray.
        """
        header = "Fray | Player | Current Guild | Wins | Losses | Winrate\n"
        header += "--|--|--|--|--|--"
        print(header)
        for fray in self.unique_frays:
            self.get_best_player_in_fray(fray)

    def get_best_player_in_fray(self, fray):
        """
        Print a markdown table row with info about the best player for
        a fray.
        """
        players, wins, losses, wrs = self._fray_to_arrays(fray)
        fn = self.unique_fray_names[fray]
        J = np.argmax(wins)
        strr = (f"#{fn} | @{players[J]} | {get_player_guild(players[J])}"
                + f" | {wins[J]} | {losses[J]} | {round(100*wrs[J])}")
        print(strr)

    def get_best_in_tier(self):
        """
        Print markdown table with the 25 best brawlers in this tier.
        """
        player_data = {}
        for fray in self.unique_frays:
            players_, wins_, losses_, _ = self._fray_to_arrays(fray)
            for p, w, l in zip(players_, wins_, losses_):
                d = {"wins": w, "losses": l}
                if p in player_data.keys():
                    for k, v in d.items():
                        player_data[p][k] += v
                else:
                    player_data[p] = d
        players = np.array(list(player_data.keys()))
        wins = np.array([x['wins'] for x in player_data.values()])
        losses = np.array([x['losses'] for x in player_data.values()])
        battles = wins+losses
        threshold = 0.5*(battles).max()
        wrs = wins/battles
        wrs[battles < threshold] = 0
        J = np.argsort(wrs)[::-1]
        header = "Rank | Player | Current Guild | Wins | Losses | Winrate\n"
        header += "--|--|--|--|--|--"
        print(header)
        for i, j in enumerate(J[:25]):
            row = (f"#{i} | @{players[j]} | {get_player_guild(players[j])}"
                   + f" | {wins[j]} | {losses[j]} | {round(100*wrs[j])}")
            print(row)


tier_3_history = BrawlHistory(tier=3)
tier_4_history = BrawlHistory(tier=4)
tier_5_history = BrawlHistory(tier=5)

for g in guild_list:
    G = Guild(g['id'])
    GUILD_ID = g['id']
    print(f"Processing/downloading data for {G.name}")
    brawl_records = None
    while brawl_records is None:
        brawl_records = G.get_brawl_records()
        time.sleep(1)
    for b in brawl_records:
        BRAWL_ID = b['tournament_id']
        download_brawl_data(GUILD_ID, BRAWL_ID)
        brawl = Brawl(GUILD_ID, BRAWL_ID,
                      brawl_data=load_brawl_data(GUILD_ID, BRAWL_ID))
        tier_3_history.add_data(brawl)
        tier_4_history.add_data(brawl)
        tier_5_history.add_data(brawl)

tier_5_history.get_best_in_tier()
print()
tier_5_history.print_best_in_frays()
print("\n\n")
tier_4_history.get_best_in_tier()
print()
tier_4_history.print_best_in_frays()
print("\n\n")
tier_3_history.get_best_in_tier()
print()
tier_3_history.print_best_in_frays()
