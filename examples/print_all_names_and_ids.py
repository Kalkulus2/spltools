import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from spltools.carddata import get_card_data

card_data = get_card_data()
for card_id, card in card_data.items():
    print(f"id: {card_id}, name: {card['name']}")
