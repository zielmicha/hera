from __future__ import print_function
import sys
import os
import pprint

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import heraclient

pprint.pprint(heraclient.get_cluster())
