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
        self.summoner_uid = data['summoner']['uid']
        self.monster_uids = [x['uid'] for x in data['monsters']]

    def get_names(self, carddata, suffix=''):
        if carddata is None:
            carddata = get_card_data()
        return ([carddata[self.summoner_id]['name']+suffix] +
                [carddata[x]['name']+suffix for x in self.monster_ids])

    def hive_images(self, width=100, height=140, card_data=None):
        if card_data is None:
            card_data = get_card_data()
        strr = hive_image(self.summoner_id, self.summoner_level, width, height,
                          card_data=card_data)
        for m, l in zip(self.monster_ids, self.monster_levels):
            strr += f" {hive_image(m, l, width, height, card_data=card_data)}"
        return strr


class Battle:
    def __init__(self, bqid=None, data=None, save_dir=None, card_data=None):
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
        self.data = data
        self.card_data = card_data
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
        self.names = {}
        t1_names = self.team1.get_names(self.card_data, suffix=" (blue)")
        t2_names = self.team2.get_names(self.card_data, suffix=" (red)")
        for i, uid in enumerate([self.team1.summoner_uid]
                                + self.team1.monster_uids):
            self.names[uid] = t1_names[i]
        for i, uid in enumerate([self.team2.summoner_uid]
                                + self.team2.monster_uids):
            self.names[uid] = t2_names[i]

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
            strr += f"##### {self.player1}'s team: \n"
            strr += self.team1.hive_images(card_data=card_data)
            strr += f"\n##### {self.player2}'s team: \n"
            strr += self.team2.hive_images(card_data=card_data)
        return strr

    def get_log(self, markdown=False):
        BLP = BattleLogParser(self.data, self, markdown=markdown)
        return BLP.text


class BattleLogParser():
    def __init__(self, data, battle, markdown=False):
        self.data = data
        self.markdown = markdown
        self.details = json.loads(data['details'])
        self.pre_battle = self.details['pre_battle']
        self.rounds = self.details['rounds']
        self.battle_id = battle.bqid1
        self.url = battle.url
        self.player1 = battle.player1
        self.player2 = battle.player2
        self.active = battle.active
        self.inactive = battle.inactive
        self.team1 = battle.team1
        self.team2 = battle.team2
        self.separator = "-"*124+"\n"
        self.text = ""
        self.ruleset = battle.ruleset
        self.names = battle.names
        self.round = 1
        self.column_header = self.construct_row(
            ["Round", "Initiator", "Action", "Target", "Value", "Hit chance",
             "RNG"])
        if self.markdown:
            self.column_header += "-|-|-|-|-|-|-\n"
        self.add_header()
        self.add_prebattle()
        # Round lines
        for r in self.rounds:
            self.text += "\n"
            if not self.markdown:
                self.text += self.separator
            self.text += self.column_header
            if not self.markdown:
                self.text += self.separator
            self.add_round(r)

    def construct_row(self, columns):
        if self.markdown:
            for i, c in enumerate(columns):
                if c == "":
                    columns[i] = "&nbsp;"
        if not isinstance(columns[6], str):
            columns[6] = f"{columns[6]:>5.3f}"
        for i, c in enumerate(columns):
            columns[i] = str(c)
        c1, c2, c3, c4, c5, c6, c7 = columns
        row = (f"{c1:>7s} | {c2:>30s} | {c3:>16s} | {c4:>30s} |"
               + f" {c5:>5s} | {c6:>11s} | {c7:>5s}\n")
        return row

    def add_header(self):
        strr = ""
        strr += (f"### {self.player1} vs {self.player2}\n"
                 + f"Battle {self.url}\n")
        strr += (f"Mana: {self.data['mana_cap']}\nRules: "
                 + f"{', '.join(self.ruleset)}\n"
                 + f"Active elements: {', '.join(self.inactive)}\n")
        if self.markdown:
            self.text += strr.replace("\n", "\n\n")
        else:
            self.text += strr
        if not self.markdown:
            self.text += self.separator
        self.text += self.column_header
        if not self.markdown:
            self.text += self.separator

    def get_round_string(self):
        return f"{self.round:>3d}-{self.round_count:<3d}"

    def get_empty_round_string(self):
        return ""

    def add_prebattle(self):
        self.round_count = 1
        for a in self.pre_battle:
            self.add_action(a)
            self.round_count += 1

    def add_round(self, round_):
        actions = round_['actions']
        self.round = round_['num']
        for ia, a in enumerate(actions):
            self.round_count = ia
            self.add_action(a)

    def add_action(self, action):
        keys = action.keys()
        if 'initiator' in keys and "target" in keys:
            if "details" in keys:
                self.action_itd(action)
            else:
                self.action_it(action)
        elif 'initiator' in keys and "group_state" in keys:
            self.action_igs(action)
        else:
            if 'group_state' in keys:
                self.action_noi_gs(action)
            else:
                self.action_woi(action)

    def action_itd(self, a):
        # with initiator, target and details
        columns = [self.get_round_string(), self.names[a['initiator']],
                   a['details']['name'], self.names[a['target']], '', '', '']
        self.text += self.construct_row(columns)

    def action_woi(self, a):
        # without initiator
        columns = [self.get_round_string(), '', a['type'],
                   self.names[a['target']], '', '', '']
        if "damage" in a.keys():
            columns[4] = a['damage']
        self.text += self.construct_row(columns)

    def action_it(self, a):
        # ~ print(list(a.keys()))
        columns = [self.get_round_string(), self.names[a['initiator']],
                   a['type'], self.names[a['target']], '', '', '']
        if "damage" in a.keys():
            columns[4] = a['damage']
            if "hit_chance" in a.keys():
                columns[5:] = [a['hit_chance'], a['hit_val']]
        self.text += self.construct_row(columns)

    def get_summoner_buff_targets(self, a, rev=False):
        ini = a['initiator']
        if rev:
            targets = [self.names[x] for x in
                       (self.team2.monster_uids
                        if ini == self.team1.summoner_uid
                        else self.team1.monster_uids)]
        else:
            targets = [self.names[x] for x in
                       (self.team1.monster_uids
                        if ini == self.team1.summoner_uid
                        else self.team2.monster_uids)]
        return targets

    def action_igs(self, a):
        targets = [self.names[x['monster']] for x in a['group_state']]
        name = a['details']['name']
        columns = [self.get_round_string()] + [""]*6
        if name == "Summoner":
            if "stats" in a['details'].keys():
                stats = a['details']['stats']
                if stats:
                    columns = [self.get_round_string()] + [""]*6
                    v = list(stats.values())[0]
                    sum_buff_name = f"{v:+} {list(stats.keys())[0]}"
                    targets = self.get_summoner_buff_targets(a, rev=v < 0)
                    columns[1:4] = [self.names[a['initiator']], sum_buff_name,
                                    targets[0]]
                    self.text += self.construct_row(columns)
                    for t in targets[1:]:
                        columns = [self.get_empty_round_string(), '', '', t,
                                   '', '', '']
                        self.text += self.construct_row(columns)
            if "ability" in a['details'].keys():
                columns = [self.get_round_string()] + [""]*6
                ability = a['details']['ability']
                if ability in ("Resurrect", "Cleanse"):
                    return
                targets = self.get_summoner_buff_targets(a)
                columns[1:4] = [self.names[a['initiator']], ability,
                                targets[0]]
                self.text += self.construct_row(columns)
                for t in targets[1:]:
                    columns = [self.get_empty_round_string(), '', '', t, '', '',
                               '']
                    self.text += self.construct_row(columns)
        else:
            type_ = a['type']
            if type_ in ("buff", "halving"):
                columns[1:3] = [self.names[a['initiator']],
                                a['details']['name']]
                columns[3] = targets[0] if len(targets) > 0 else ''
                self.text += self.construct_row(columns)
                if len(targets) > 1:
                    for t in targets[1:]:
                        columns = [self.get_empty_round_string(), '', '', t,
                                   '', '', '']
                        self.text += self.construct_row(columns)
            elif type_ == "remove_buff":
                remove_string = ('remove ' + a['details']['name'])[:16]
                columns[1:3] = [self.names[a['initiator']], remove_string]
                self.text += self.construct_row(columns)
            else:
                print("Unhandled:", a)

    def action_noi_gs(self, a):
        targets = [self.names[x['monster']] for x in a['group_state']]
        name = a['type']
        columns = [self.get_round_string(), "", name] + [""]*4
        if 'dmg' in a['group_state'][0].keys():
            dmg = a['group_state'][0]['dmg']
            columns[3:5] = [targets[0], dmg]
            self.text += self.construct_row(columns)
            for it, t in enumerate(targets[1:]):
                dmg = a['group_state'][it+1]['dmg']
                columns = [self.get_empty_round_string(), '', '', t, dmg, '',
                           '']
                self.text += self.construct_row(columns)
        else:
            print("Unhandled:", a)
