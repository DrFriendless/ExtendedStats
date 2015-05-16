# configuration for a particular stats site

# the directory where the configuration files (e.g. usernames.txt) are stored
cfgdir = "/home/john/geek/"

# the directory where files downloaded from BGG are stored - not related to the MySQL database
# this must end with the file separator char
dbdir = "/home/john/geek/db/"

# the directory where generated files are written - Apache will serve files from here.
resultdir = "/home/john/geek/result/"

# the password for the database
password = "basilisk"

# the host the database runs on
dbhost = "localhost"

# the user to log into the database as
dbuser = "root"

# the name of the database
dbname = "extended"

# users subject to testing - must be an enrolled user
debugUsers = ["Friendless", "Almecho"]

# the internet-visible address of this service - used for when the downloader wants to copy stuff
# from the dynamic web site
site = "http://friendlessstats.dtdns.net/"
