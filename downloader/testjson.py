#! /usr/bin/env python
import sys
sys.path.append(".")

"""This class is to test the JSON API without doing all the work of a full test."""

USERS = [ "Friendless", "sa266", "spellenclub ST", "PzVIE", "Damjon", "yzemaze" ]
TAGS = ["pbpy", "obpy", "rbpy", "mmmpie", "pogo", "pogotable", "mostunplayed", "playrate", "playrateown", "playrateprev",
        "pbmever", "pbmytd", "pbmgraph", "pr", "pbq", "favourites", "fgbpy", "bestdays", "ratingByRanking", "unusual", "least",
        "shouldplay", "shouldplayown", "timeline", "thm", "thd", "thday", "dimesbydesigner", "florence", "streaks",
        "pby", "consistency", "morepie", "generic", "playsByRanking", "yearly" ]
CHOOSE_URL = "%sdynamic/choose/%s/%s"
JSON_URL = "%sdynamic/json/%s/%s"

import urllib, time, sitedata
errors = []
all = [ ]
for user in USERS:
    for tag in TAGS:
        all.append(JSON_URL % (sitedata.site, user, tag))
total = len(all)
i = 0
for s in all:
    i += 1
    start = time.time()
    print "%d/%d %s" % (i, total, s),
    response = urllib.urlopen(s)
    end = time.time()
    print " (%s seconds) " % int(end-start), response.code
    if response.code != 200:
        errors.append(s)
if len(errors) > 0:
    print
    print "FAILURES"
    for e in errors:
        print e
print
print "JSON functionality is %d%% working!" % ((len(all) - len(errors)) * 100 / len(all))
