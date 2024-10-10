import os
import sys
from numpy import argsort
sys.path.insert(0, os.path.abspath('..'))
from spltools import MinorChest, MajorChest, UltimateChest

minor_chest = MinorChest()
major_chest = MajorChest()
ultimate_chest = UltimateChest()

minor_chest_batches = [MinorChest(batch=b) for b in range(1, 4)]
major_chest_batches = [MajorChest(batch=b) for b in range(1, 4)]
ultimate_chest_batches = [UltimateChest(batch=b) for b in range(1, 4)]

# Rarity draws
common_draw_batch_cost = [150*1.5**x for x in range(1, 4)]
rare_draw_batch_cost = [750*1.5**x for x in range(1, 4)]
epic_draw_batch_cost = [7500*1.5**x for x in range(1, 4)]
legendary_draw_batch_cost = [35000*1.5**x for x in range(1, 4)]

completion = {"common": 0.0, "rare": 0.0, "epic": 0.0, "legendary": 0.0}
relative_value_factor = {}
norm = sum([(1-x) for x in completion.values()])/4
for k, v in completion.items():
    relative_value_factor[k] = (1-v)/norm

values = {"legendary_potions": 0,
          "alchemy_potions": 0,
          "energy": 1000,
          "jackpot": 100000,
          "merits": 1,
          "common_rf": 150*relative_value_factor['common'],
          "rare_rf": 750*relative_value_factor['rare'],
          "epic_rf": 7500*relative_value_factor['epic'],
          "legendary_rf": 35000*relative_value_factor['legendary'],
          "common_gf": 625,
          "rare_gf": 2500,
          "epic_gf": 12500,
          "legendary_gf": 62500
          }


def get_chest_value(chest, item_values):
    """
    Calculate the value of a chest given the item values identified
    in item values. Requires that item_values has a value for each
    element returned by chest.average_draw()
    """
    value = 0
    for k, v in chest.average_draw().items():
        value += item_values[k]*v
    return value


minor_chest_value = get_chest_value(minor_chest, values)
major_chest_value = get_chest_value(major_chest, values)
ultimate_chest_value = get_chest_value(ultimate_chest, values)

draw_value = {}
costs = {}
for i, c in enumerate(minor_chest_batches):
    key = f"Minor chest batch {i+1}"
    draw_value[key] = minor_chest_value
    costs[key] = c.cost
for i, c in enumerate(major_chest_batches):
    key = f"Major chest batch {i+1}"
    draw_value[key] = major_chest_value
    costs[key] = c.cost
for i, c in enumerate(ultimate_chest_batches):
    key = f"Ultimate chest batch {i+1}"
    draw_value[key] = ultimate_chest_value
    costs[key] = c.cost
for i, c in enumerate(common_draw_batch_cost):
    key = f"Common draw batch {i+1}"
    draw_value[key] = 0.96*values['common_rf'] + 0.04*values['common_gf']
    costs[key] = c
for i, c in enumerate(rare_draw_batch_cost):
    key = f"Rare draw batch {i+1}"
    draw_value[key] = 0.96*values['rare_rf'] + 0.04*values['rare_gf']
    costs[key] = c
for i, c in enumerate(epic_draw_batch_cost):
    key = f"Epic draw batch {i+1}"
    draw_value[key] = 0.96*values['epic_rf'] + 0.04*values['epic_gf']
    costs[key] = c
for i, c in enumerate(legendary_draw_batch_cost):
    key = f"Legendary draw batch {i+1}"
    draw_value[key] = 0.96*values['legendary_rf'] + 0.04*values['legendary_gf']
    costs[key] = c

value_per_cost = {}
for k, value in draw_value.items():
    value_per_cost[k] = value/costs[k]
y = list(value_per_cost.values())
x = list(value_per_cost.keys())

sorted_index = argsort(y)[::-1]
print("Glint spending strategy")
print("-----------------------")
for j, index in enumerate(sorted_index):
    print(f"{j+1}. {x[index]}")
