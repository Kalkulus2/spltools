from os.path import isfile, isdir
from os import makedirs
from spltools.settings import BATTLE_URL, BATTLE_LINK_URL, request_session
from spltools.carddata import hive_image, get_card_data
import json


def get_battle_data(bqid, save_dir=None):
    """
    Downloads battle data and optionally saves it to file.

    Parameters
    ----------
    bqid : str
        Battle queue id
    save_dir : str
        (Optional) If provided, the data will be saved in this
        directory with file name equal to the bqid. Creates the
        directory if it does not exist.
    """
    fp = f"{save_dir}/{bqid}"
    url = f"{BATTLE_URL}/result?id={bqid}"
    if save_dir is not None:
        if not isdir(save_dir):
            makedirs(save_dir)
        if isfile(fp):
            with open(fp, "r") as iF:
                data = json.load(iF)
                return data
    data = request_session.get(url)
    if data:
        data = data.json()
        if save_dir is not None:
            with open(fp, "w") as oF:
                json.dump(data, oF)
        return data
    else:
        return None


class Team:
    def __init__(self, data):
        self.summoner_id = data['summoner']['card_detail_id']
        self.summoner_level = data['summoner']['level']
        self.monster_ids = [x['card_detail_id'] for x in data['monsters']]
        self.monster_levels = [x['level'] for x in data['monsters']]

    def get_names(self, carddata):
        return carddata[self.summoner_id]['name'], \
               [carddata[x]['name'] for x in self.monster_ids]

    def hive_images(self, width=100, height=140, card_data=None):
        if card_data is None:
            card_data = get_card_data()
        strr = hive_image(self.summoner_id, self.summoner_level, width, height,
                          card_data=card_data)
        for m, l in zip(self.monster_ids, self.monster_levels):
            strr += f" {hive_image(m, l, width, height, card_data=card_data)}"
        return strr


class Battle:
    def __init__(self, bqid=None, data=None, save_dir=None):
        if data is None:
            data = get_battle_data(bqid, save_dir)
        if data is None:
            self.valid = False
            self.errmsg = f"Could not fetch battle data for id: {bqid}"
            return
        if isinstance(data, str):
            self.valid = False
            self.errmsg = data
            return
        self.bqid1 = data['battle_queue_id_1']
        self.bqid2 = data['battle_queue_id_2']
        self.player1, self.player2 = data['player_1'], data['player_2']
        self.details = json.loads(data['details'])
        self.match_type = data['match_type']
        self.format = data['format']
        if self.format is None:
            self.format = "Wild"
        if ('tournament' in data.keys()
                and 'sub_format' in data['tournament'].keys()
                and data['tournament']['sub_format'] == "brawl"):
            self.format = "Brawl"
        all_colors = ["Red", "Blue", "Green", "White", "Black", "Gold"]
        self.inactive = data['inactive'].split(",")
        self.active = [x for x in all_colors if x not in self.inactive]
        self.ruleset = data['ruleset'].split("|")
        self.mana_cap = data['mana_cap']
        self.winner = self.details['winner']

        self.team1 = Team(self.details['team1'])
        self.team2 = Team(self.details['team2'])

        self.url = f"{BATTLE_LINK_URL}/{self.bqid1}"
        self.valid = True

    def markdown_summary(self, images=True, card_data=None):
        if not self.valid:
            return self.errmsg
        strr = f"[{self.player1} vs. {self.player2}]({self.url})||\n"
        strr += "-|-\n"
        strr += f"Type | {self.match_type}\n"
        strr += f"Format | {self.format.capitalize()}\n"
        strr += f"Mana | {self.mana_cap}\n"
        strr += f"Elements | {', '.join(self.active)}\n"
        strr += f"Rules | {', '.join(self.ruleset)}\n"
        strr += f"Winner | {self.winner}\n"
        if images:
            if card_data is None:
                card_data = get_card_data()
            strr += f"##### {self.player1}'s team:\n"
            strr += self.team1.hive_images(card_data=card_data)
            strr += f"\n##### {self.player2}'s team:\n"
            strr += self.team2.hive_images(card_data=card_data)
        return strr
