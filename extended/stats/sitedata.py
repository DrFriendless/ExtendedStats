# configuration for a particular stats site
import os, sys

# the directory where the configuration files (e.g. usernames.txt) are stored, and where sitesettings.py is.
installDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(installDir)
from sitesettings import *

dbdir = os.path.join(installDir, "db")

