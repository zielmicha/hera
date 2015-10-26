from __future__ import print_function
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import argparse
import heraclient

disk = heraclient.new_disk(size='10M')

heraclient.Sandbox.create(timeout=15, disk=disk,
                          async=True,
                          webhook_url='http://requestb.in/13mhz4b1')
