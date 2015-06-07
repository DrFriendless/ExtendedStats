# configuration for a particular stats site
import os, sys

downloaderDir = os.path.split(os.path.realpath(__file__))[0]
installDir = os.path.split(downloaderDir)[0]
# the directory where the configuration files (e.g. usernames.txt) are stored
cfgdir = installDir
dbdir = os.path.join(installDir, "db")
resultdir= os.path.join(installDir, "static")
logfile = os.path.join(installDir, "downloader.log")

if not os.path.exists(dbdir):
    os.makedirs(dbdir)
if not os.path.exists(resultdir):
    os.makedirs(resultdir)

# the password for the database
password = "basilisk"

# the host the database runs on
dbhost = "localhost"

# the user to log into the database as
dbuser = "root"

# the name of the database
dbname = "extended"

# the internet-visible address of this service - used for when the downloader wants to copy stuff
# from the dynamic web site
site = "http://friendlessstats.dtdns.net/"
