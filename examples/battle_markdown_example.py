import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import spltools

b = spltools.Battle("sl_651debdfd690ddd9eacaa0c88bd9820d", save_dir="battles")
print(b.markdown_summary())
