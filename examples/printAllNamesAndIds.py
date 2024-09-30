import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from spltools.carddata import getCardData

carddata = getCardData()
for c in carddata:
    print(f"id: {c['id']}, name: {c['name']}")
