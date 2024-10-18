import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from spltools import Brawl

"""
Instantiate a Brawl object with my guild's id and the brawl id.
You can find brawl id's the easiest by going to splex.gg, clicking into
your guild, and looking at the list of past brawls. The brawl id is
listed in the second column.
"""
b = Brawl("92c2bf80a4a64d70959eb51d6fbd974fdf76fb48",
          "GUILD-BC251-BL78-BRAWL5")
b.print_results()
print("\n")
print(b.markdown_results_and_payouts())
