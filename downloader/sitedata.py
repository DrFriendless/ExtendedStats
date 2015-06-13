# configuration for a particular stats site
import os, sys

# the directory where the configuration files (e.g. usernames.txt) are stored, and where sitesettings.py is.
installDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.append(installDir)
from sitesettings import *

downloaderDir = os.path.join(installDir, "downloader")
dbdir = os.path.join(installDir, "db")
resultdir= os.path.join(installDir, "static")
logfile = os.path.join(installDir, "downloader.log")


