import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from spltools.carddata import get_card_data, in_set

card_data = get_card_data()
c1, c2, c3 = "Card", "Alpha", "Beta"
c4, c5, c6, c7 =  "Untamed", "Gladius", "Chaos", "Rebellion"
print(
    f"{c1:^23s} | {c2:^5s} | {c3:^4s} | {c4:^7s} | {c5:^7s} | {c6:^5s}" \
    +f" | {c7:9s}""") 
for card_id, card in card_data.items():
    c1 = card['name'];
    c2 = "X" if in_set(card_id, "Alpha", card_data) else "" 
    c3 = "X" if in_set(card_id, "Beta", card_data) else "" 
    c4 = "X" if in_set(card_id, 4, card_data) else ""  # Untamed, using number 
    c5 = "X" if in_set(card_id, "Gladius", card_data) else "" 
    c6 = "X" if in_set(card_id, "Chaos", card_data) else "" 
    c7 = "X" if in_set(card_id, "Rebellion", card_data) else "" 
    print(
        f"{c1:^23s} | {c2:^5s} | {c3:^4s} | {c4:^7s} | {c5:^7s} | {c6:^5s}" \
        +f" | {c7:9s}""")  

