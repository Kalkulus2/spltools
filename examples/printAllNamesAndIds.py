import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from spltools.carddata import get_card_data

card_data = get_card_data()
for c in card_data:
    print(f"id: {c['id']}, name: {c['name']}")
