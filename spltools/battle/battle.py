from os.path import isfile, isdir
from os import makedirs
from spltools.settings import BATTLE_URL, BATTLE_LINK_URL, request_session
from spltools.carddata import hive_image, get_card_data
from collections import Counter
from numpy import array
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
    def __init__(self, data, pre_battle=None):
        self.data = data
        self.summoner_id = data['summoner']['card_detail_id']
        self.summoner_level = data['summoner']['level']
        self.monster_ids = [x['card_detail_id'] for x in data['monsters']]
        self.monster_levels = [x['level'] for x in data['monsters']]
        self.summoner_uid = data['summoner']['uid']
        self.monster_uids = [x['uid'] for x in data['monsters']]
        self.pre_battle = pre_battle

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

    def stats(self):
        """
        Compute the total stats for the team by summing up individual
        monster stats.

        Returns
        -------
        dict
            A dictionary containing the total values for attack,
            ranged, magic, health, armor, and speed.
        """
        stats_dict = {"attack": 0,
                      "ranged": 0,
                      "magic": 0,
                      "health": 0,
                      "armor": 0,
                      "average speed": 0,
                      "abilities": {}}
        abls = []
        n_monsters = len(self.data['monsters'])
        atks = array([x['state']['stats'][0] for x in self.data['monsters']])
        rngs = array([x['state']['stats'][1] for x in self.data['monsters']])
        mags = array([x['state']['stats'][2] for x in self.data['monsters']])
        arms = array([x['state']['stats'][3] for x in self.data['monsters']])
        hlts = array([x['state']['stats'][4] for x in self.data['monsters']])
        spds = array([x['state']['stats'][5] for x in self.data['monsters']])
        stats_dict['attack'] = sum(atks)
        stats_dict['ranged'] = sum(rngs)
        stats_dict['magic'] = sum(mags)
        stats_dict['armor'] = sum(arms)
        stats_dict['health'] = sum(hlts)
        stats_dict['average speed'] = round(sum(spds)/len(spds), 2)
        for m in self.data['monsters']:
            abls += m['state']['abilities']
        unique_attackers = sum(atks > 0)
        unique_rangers = sum(rngs > 0)
        unique_magics = sum(mags > 0)
        counter = Counter(abls)
        stats_dict['abilities'] = dict(counter)
        summoner_stats = self.data['summoner']['state']['stats']
        if "Swiftness" in counter:
            stats_dict['average speed'] += counter["Swiftness"]
        if "Inspire" in counter:
            stats_dict['attack'] += counter["Inspire"]*unique_attackers
        trained = {}
        # Look for weapons training
        for a in self.pre_battle:
            if ('details' in a.keys()
                    and a['details']['name'] == "Weapons Training"):
                gs = a['group_state']
                for m in gs:
                    other = m['state']['other']
                    for o in other:
                        if o[0] == "Trained":
                            trained[m['monster']] = o[1]
        for k, v in trained.items():
            stats_dict['attack'] += v['attack']
            stats_dict['ranged'] += v['ranged']
            stats_dict['magic'] += v['magic']
        # Look for summoner buffs for speed, health, armor
        for a in self.pre_battle:
            if (a['type'] == "buff" and 'details' in a.keys()
                    and a['details']['name'] == "Summoner"
                    and 'stats' in a['details'].keys()):
                for k, v in a['details']['stats'].items():
                    if v > 0:
                        if k == "armor":
                            stats_dict['armor'] += v*n_monsters
                        elif k == "speed":
                            stats_dict['average speed'] += v
                        elif k == "health":
                            stats_dict['health'] += v*n_monsters
        
        strr = ("Attack | Ranged | Magic | Armor | Health | Average Speed\n"
                + "-|-|-|-|-|-\n"
                + f"{stats_dict['attack']} | {stats_dict['ranged']} |"
                + f"{stats_dict['magic']} | {stats_dict['armor']} |"
                + f"{stats_dict['health']} | {stats_dict['average speed']}\n\n")

        if "Inspire" in counter and unique_attackers < 3:
            strr += ("You have a unit with Inspire but only "
                     + f"{unique_attackers} melee attackers. Consider adding "
                     + "more melee attackers to more efficiently use this "
                     + "ability.\n\n")
        if summoner_stats[0] > 0 and unique_attackers < 3:
            strr += ("You have a summoner that boosts attack but only "
                     + f"{unique_attackers} melee attackers. Consider adding "
                     + "more melee attackers to more efficiently use this "
                     + "summoner.\n\n")
        if summoner_stats[1] > 0 and unique_rangers < 3:
            strr += ("You have a summoner that boosts ranged but only "
                     + f"{unique_rangers} ranged attackers. Consider adding "
                     + "more ranged attackers to more efficiently use this "
                     + "summoner.\n\n")
        if summoner_stats[2] > 0 and unique_magics < 3:
            strr += ("You have a summoner that boosts magic but only "
                     + f"{unique_magics} magic attackers. Consider adding "
                     + "more magic attackers to more efficiently use this "
                     + "summoner.\n\n")

        if stats_dict['average speed'] < 3 and "True Strike" not in counter:
            strr += ("Your team has an average speed of "
                     + f"{stats_dict['average speed']}. This makes it "
                     + "weak against miss-based defensive strategies.")

        return stats_dict, strr


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

        self.team1 = Team(self.details['team1'], self.details['pre_battle'])
        self.team2 = Team(self.details['team2'], self.details['pre_battle'])
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
        self.tracker = {}
        for m in self.team1.monster_uids + self.team2.monster_uids:
            self.tracker[self.names[m]] = {"damage done": 0,
                                           "damage taken": 0,
                                           "healing done": 0,
                                           "armor repaired": 0,
                                           "units killed": 0}
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
            if a['type'] in ("melee attack", "ranged attack", "magic attack"):
                self.tracker[self.names[a['target']]]['damage taken'] \
                    += a['damage']
        self.text += self.construct_row(columns)

    def action_it(self, a):
        iname = self.names[a['initiator']]
        tname = self.names[a['target']]
        columns = [self.get_round_string(), iname,
                   a['type'], tname, '', '', '']
        if "damage" in a.keys():
            columns[4] = a['damage']
            if "hit_chance" in a.keys():
                columns[5:] = [round(a['hit_chance'], 2), a['hit_val']]
            if a['type'] in ("melee attack", "ranged attack", "magic attack",
                             "blast", "execute", "retaliate", "spite"):
                self.tracker[tname]['damage taken'] \
                    += a['damage']
                self.tracker[iname]['damage done'] \
                    += a['damage']
            elif a['type'].lower() in ("tank heal", "heal", "triage"):
                self.tracker[iname]['healing done'] += a['damage']
            elif a['type'].lower() == "repair":
                self.tracker[iname]['armor repaired'] += a['damage']
            if a['state']['stats'][4] == 0:
                self.tracker[iname]["units killed"] += 1
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
        if len(a['group_state']) == 0:
            if a['type'] in ('zapped', "corrosive"):
                self.text += self.construct_row(columns)
                return
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

    def get_tracker_markdown(self, team='red'):
        strr = ("Unit | Damage Done | Damage taken | Healing Done"
                + " | Armor Repaired | Units Killed\n"
                + "-|-|-|-|-|-\n")
        for k, v in self.tracker.items():
            if f"({team})" in k:
                strr += (f"{k} | {v['damage done']} | {v['damage taken']}"
                         + f" | {v['healing done']} | {v['armor repaired']}"
                         + f" | {v['units killed']}\n")
        return strr+"\n"
