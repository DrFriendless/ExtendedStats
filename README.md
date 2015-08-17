Extended Stats
==============

Extended Stats is software to implement a web site which produces board game statistics.
The site gathers data from boardgamegeek.com (with Aldie's permission) and stores it in a database.
Users can then access various views of this data which present their board gaming habits in novel ways.
The software consists of two parts - the web site (in Python using Django) and the downloader (in pretty much plain Python).
The site is pretty simple to download and install - instructions are in the various HOWTO files.
Since starting cloud experiments it has been a priority to simplify installation and configuration.

Extended Stats is a LAMP architecture - Linux, Apache, MySQL and Python.
Django is used for templating and to connect Apache to Python.

The Downloader
--------------

The downloader is the code which harvests data from boardgamegeek.com and puts it into the database.
The code for the downloader is in the downloader directory.
The downloader code is completely separate from the web site code - in particular, the downloader doesn't use any Django stuff.

The Web Site
------------

The web site code is in the directories extended and extended/stats.
The organisation of these files is pretty confusing, but that's what Django wants.
Essentially the URL patterns in urls.py point to code in views.py and imgviews.py.

 
Testing Strategy
----------------

The installation is tested by running the script testsite.py.
This assumes that there are particular users in the site - those are users with unusual data whom I have found can stress the system.
The script retrieves various URLs and tests whether the retrieval worked or not.
This is only a basic testing strategy as there's no guarantee that the results are at all correct.

In the future, I'd like to make testing more comprehensive by being able to replace the MySQL database with a SQLite database
which could be populated with fake data.
The JSON URLs (see testjson.py) could be accessed to ensure that the correct data is being returned.
At the moment the JSON data is pretty scrappy, as it's a complete hack over the top of the Django templating stuff.
As Django templating happens server side, and the JSON results are serialisations of that data that's used on the server side,
they're effectively simplified versions of server-side objects which shouldn't be exposed to clients anyway.
As I would like to move away from Django (I'm thinking Flask and AngularJS), it seems to be a reasonable migration strategy to create
more JSON-friendly objects and use them to populate the pages using whatever technology.
 