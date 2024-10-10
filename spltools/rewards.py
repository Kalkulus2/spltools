class Chest:
    """
    Base class for chests.

    Attributes
    ----------
    potion_chance : float
        Chance of the chest containing a potion.
    merit_chance: float
        Chance of the chest containing merits.
    energy_chance: float
        Chance of the chest containing energy.
    jackpot_chance: float
        Chance of the chest containing a jackpot.
    card_chance: float
        Chance of the chest containing a card.
    gold_foil_chance: float
        Chance for a card draw to result in a gold foil card.
    base_cost : int
        Glint cost of the first batch of this chest type.
    cost : int
        Glint cost of this batch (defined in the initializer) of
        chests.
    common_card_chance : float
        Chance of drawing a common card if the chest contains a card.
    rare_card_chance : float
        Chance of drawing a rare card if the chest contains a card.
    epic_card_chance : float
        Chance of drawing an epic card if the chest contains a card.
    legendary_card_chance : float
        Chance of drawing a legendary card if the chest contains a
        card.
    common_multiplier_rf : 2-tuple of float
        The minimum and maximum amount of common regular foil cards
        that can be gained in this chest.
    rare_multiplier_rf : 2-tuple of float
        The minimum and maximum amount of rare regular foil cards
        that can be gained in this chest.
    epic_multiplier_rf : 2-tuple of float
        The minimum and maximum amount of epic regular foil cards
        that can be gained in this chest.
    legendary_multiplier_rf : 2-tuple of float
        The minimum and maximum amount of legendary regular foil cards
        that can be gained in this chest.
    common_multiplier_gf : 2-tuple of float
        The minimum and maximum amount of common gold foil cards
        that can be gained in this chest.
    rare_multiplier_gf : 2-tuple of float
        The minimum and maximum amount of common gold foil cards
        that can be gained in this chest.
    epic_multiplier_gf : 2-tuple of float
        The minimum and maximum amount of common gold foil cards
        that can be gained in this chest.
    legendary_multiplier_gf : 2-tuple of float
        The minimum and maximum amount of common gold foil cards
        that can be gained in this chest.
    potion_multiplier = 2-tuple of float
        The minimum and maximum amount of potions that can be gained
        in this chest.
    merits_multiplier = 2-tuple of float
        The minimum and maximum amount of merits that can be gained
        in this chest.
    energy_multiplier = 2-tuple of float
        The minimum and maximum amount of energy that can be gained
        in this chest.
    """
    def __init__(self, potion_chance, merit_chance, energy_chance,
                 jackpot_chance, base_cost, batch, common_card_chance,
                 rare_card_chance, epic_card_chance, legendary_card_chance,
                 common_multiplier_rf, rare_multiplier_rf, epic_multiplier_rf,
                 legendary_multiplier_rf, common_multiplier_gf,
                 rare_multiplier_gf, epic_multiplier_gf,
                 legendary_multiplier_gf, potion_multiplier, merits_multiplier,
                 energy_multiplier):
        self.potion_chance = potion_chance
        self.merit_chance = merit_chance
        self.energy_chance = energy_chance
        self.jackpot_chance = jackpot_chance
        self.card_chance = 0.33
        self.gold_foil_chance = 0.02
        self.base_cost = base_cost
        self.batch = batch
        self.cost = base_cost*1.5**(batch-1)
        self.common_card_chance = common_card_chance
        self.rare_card_chance = rare_card_chance
        self.epic_card_chance = epic_card_chance
        self.legendary_card_chance = legendary_card_chance
        self.common_multiplier_rf = common_multiplier_rf
        self.rare_multiplier_rf = rare_multiplier_rf
        self.epic_multiplier_rf = epic_multiplier_rf
        self.legendary_multiplier_rf = legendary_multiplier_rf
        self.common_multiplier_gf = common_multiplier_gf
        self.rare_multiplier_gf = rare_multiplier_gf
        self.epic_multiplier_gf = epic_multiplier_gf
        self.legendary_multiplier_gf = legendary_multiplier_gf
        self.potion_multiplier = potion_multiplier
        self.merits_multiplier = merits_multiplier
        self.energy_multiplier = energy_multiplier

    def _apply_potions(self, legendary_potion=True, alchemy_potion=True):
        """
        Apply legendary and alchemy potions to the card draws.
        (Doubles chances of epic and legendary cards)

        Parameters
        ----------
        legendary_potion: bool
            True (default) for using legendary potions.
        alchemy_potion: bool
            True (default) for using alchemy potions.

        Returns
        -------
        None

        """
        if legendary_potion:
            self.common_card_chance -= self.epic_card_chance
            self.common_card_chance -= self.legendary_card_chance
            self.epic_card_chance *= 2
            self.legendary_card_chance *= 2
        if alchemy_potion:
            self.gold_foil_chance *= 2

    def average_draw(self):
        """
        Returns the average result of a single draw.

        Parameters
        ----------
        None

        Returns
        -------
        result : dict
            Dictionary of chest rewards, with item names as keys and
            item amount as values.
        """

        out = {}
        out['legendary_potions'] = (0.5*self.potion_chance
                                    * 0.5*sum(self.potion_multiplier))
        out['alchemy_potions'] = out['legendary_potions']
        out['energy'] = self.energy_chance*0.5*sum(self.energy_multiplier)
        out['jackpot'] = self.jackpot_chance
        out['merits'] = self.merit_chance*sum(self.merits_multiplier)
        out['common_rf'] = (self.card_chance*self.common_card_chance
                            * (1 - self.gold_foil_chance)
                            * 0.5*sum(self.common_multiplier_rf))
        out['rare_rf'] = (self.card_chance*self.rare_card_chance
                          * (1 - self.gold_foil_chance)
                          * 0.5*sum(self.rare_multiplier_rf))
        out['epic_rf'] = (self.card_chance*self.epic_card_chance
                          * (1 - self.gold_foil_chance)
                          * 0.5*sum(self.epic_multiplier_rf))
        out['legendary_rf'] = (self.card_chance*self.legendary_card_chance
                               * (1 - self.gold_foil_chance)
                               * 0.5*sum(self.legendary_multiplier_rf))
        out['common_gf'] = (self.card_chance*self.common_card_chance
                            * (self.gold_foil_chance)
                            * 0.5*sum(self.common_multiplier_gf))
        out['rare_gf'] = (self.card_chance*self.rare_card_chance
                          * (self.gold_foil_chance)
                          * 0.5*sum(self.rare_multiplier_gf))
        out['epic_gf'] = (self.card_chance*self.epic_card_chance
                          * (self.gold_foil_chance)
                          * 0.5*sum(self.epic_multiplier_gf))
        out['legendary_gf'] = (self.card_chance*self.legendary_card_chance
                               * (self.gold_foil_chance)
                               * 0.5*sum(self.legendary_multiplier_gf))
        return out


class MinorChest(Chest):
    """
    Minor chest class. Inherits Chest.
    """

    def __init__(self, batch=1, legendary_potion=True, alchemy_potion=True):
        super().__init__(potion_chance=0.31999, merit_chance=0.3,
                         energy_chance=0.05, jackpot_chance=0.00001,
                         base_cost=200, batch=batch, common_card_chance=0.789,
                         rare_card_chance=0.2, epic_card_chance=0.01,
                         legendary_card_chance=0.001,
                         common_multiplier_rf=(1, 1),
                         rare_multiplier_rf=(1, 1),
                         epic_multiplier_rf=(1, 1),
                         legendary_multiplier_rf=(1, 1),
                         common_multiplier_gf=(1, 1),
                         rare_multiplier_gf=(1, 1),
                         epic_multiplier_gf=(1, 1),
                         legendary_multiplier_gf=(1, 1),
                         potion_multiplier=(1, 1),
                         merits_multiplier=(20, 180),
                         energy_multiplier=(1, 1))
        self._apply_potions(legendary_potion, alchemy_potion)


class MajorChest(Chest):
    """
    Major chest class. Inherits Chest.
    """
    def __init__(self, batch=1, legendary_potion=True, alchemy_potion=True):
        super().__init__(potion_chance=0.3099, merit_chance=0.26,
                         energy_chance=0.1, jackpot_chance=0.0001,
                         base_cost=1000, batch=batch, common_card_chance=0.76,
                         rare_card_chance=0.2, epic_card_chance=0.03,
                         legendary_card_chance=0.01,
                         common_multiplier_rf=(2, 6),
                         rare_multiplier_rf=(1, 5),
                         epic_multiplier_rf=(1, 2),
                         legendary_multiplier_rf=(1, 1),
                         common_multiplier_gf=(1, 3),
                         rare_multiplier_gf=(1, 3),
                         epic_multiplier_gf=(1, 2),
                         legendary_multiplier_gf=(1, 1),
                         potion_multiplier=(3, 7),
                         merits_multiplier=(250, 750),
                         energy_multiplier=(1, 4))
        self._apply_potions(legendary_potion, alchemy_potion)


class UltimateChest(Chest):
    """
    Ultimate chest class. Inherits Chest.
    """
    def __init__(self, batch=1, legendary_potion=True, alchemy_potion=True):
        super().__init__(potion_chance=0.269, merit_chance=0.2,
                         energy_chance=0.2, jackpot_chance=0.001,
                         base_cost=4500, batch=batch, common_card_chance=0.688,
                         rare_card_chance=0.2, epic_card_chance=0.08,
                         legendary_card_chance=0.032,
                         common_multiplier_rf=(5, 11),
                         rare_multiplier_rf=(3, 9),
                         epic_multiplier_rf=(1, 2),
                         legendary_multiplier_rf=(1, 2),
                         common_multiplier_gf=(2, 6),
                         rare_multiplier_gf=(2, 6),
                         epic_multiplier_gf=(1, 2),
                         legendary_multiplier_gf=(1, 2),
                         potion_multiplier=(5, 15),
                         merits_multiplier=(1000, 3000),
                         energy_multiplier=(3, 5))
        self._apply_potions(legendary_potion, alchemy_potion)
