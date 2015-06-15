#! /usr/bin/env python

USERS = [ "Friendless", "sa266", "spellenclub ST", "PzVIE", "Damjon" ]
#USERS = [ "Damjon" ]
URLS = [ 
        "http://friendlessstats.dtdns.net/dynamic/result/%s",
        "http://friendlessstats.dtdns.net/dynamic/tabbed/%s/1",
        "http://friendlessstats.dtdns.net/dynamic/tabbed/%s/2",
        "http://friendlessstats.dtdns.net/dynamic/tabbed/%s/3",
        "http://friendlessstats.dtdns.net/dynamic/tabbed/%s/4",
        "http://friendlessstats.dtdns.net/dynamic/tabbed/%s/5",        
        "http://friendlessstats.dtdns.net/dynamic/tabbed/%s/6",        
        "http://friendlessstats.dtdns.net/dynamic/image/pbq/%s",
        "http://friendlessstats.dtdns.net/dynamic/image/fpvr/%s",
        "http://friendlessstats.dtdns.net/dynamic/plays/%s/florence/lastyear",
        "http://friendlessstats.dtdns.net/dynamic/image/morgan/%s",
        "http://friendlessstats.dtdns.net/dynamic/image/pogo/%s",
        "http://friendlessstats.dtdns.net/dynamic/crazy/%s",
        "http://friendlessstats.dtdns.net/dynamic/numplayers/%s",
        "http://friendlessstats.dtdns.net/dynamic/series/%s",
        "http://friendlessstats.dtdns.net/dynamic/cat/%s/designer",
        "http://friendlessstats.dtdns.net/dynamic/cat/%s/mechanic",
        "http://friendlessstats.dtdns.net/dynamic/cat/%s/category",
        "http://friendlessstats.dtdns.net/dynamic/image/lag/%s",
        "http://friendlessstats.dtdns.net/dynamic/unusual/%s",
        "http://friendlessstats.dtdns.net/dynamic/checklist/%s",
        "http://friendlessstats.dtdns.net/dynamic/multiyear/%s",
        "http://friendlessstats.dtdns.net/dynamic/locations/%s",
        "http://friendlessstats.dtdns.net/dynamic/plays/%s/totals",
        "http://friendlessstats.dtdns.net/dynamic/yearcomparison/%s",
        "http://friendlessstats.dtdns.net/dynamic/updates/%s",
        "http://friendlessstats.dtdns.net/dynamic/year/%s/2012",
        "http://friendlessstats.dtdns.net/dynamic/trade/%s",
        "http://friendlessstats.dtdns.net/dynamic/image/newPlays/%s",
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s",
        "http://friendlessstats.dtdns.net/dynamic/image/pbm/%s",
        "http://friendlessstats.dtdns.net/dynamic/playscsv/%s",
        "http://friendlessstats.dtdns.net/dynamic/multiyear/%s",
        "http://friendlessstats.dtdns.net/dynamic/ipod/%s",
        "http://friendlessstats.dtdns.net/dynamic/image/lbr/%s",
        "http://friendlessstats.dtdns.net/dynamic/dimesbydesigner/%s",
        # want in trade or on wishlist
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/want/wishlist/1234/or",
        # All Peter Hawes games
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/designer/770",        
        # All games on your wishlist
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/wishlist/12345",        
        # Owned Knizia games
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/designer/2/owned/and",
        # Kramer without Kiesling
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/designer/7/designer/42/minus",
        # Either of the Brunos
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/designer/125/designer/1727/or",
        # previously owned modular board mechanic
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/mechanic/Modular Board/prevowned/and",
        # adventure category
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/category/Adventure",
        # plays of owned Knizias
        "http://friendlessstats.dtdns.net/dynamic/image/pogo/%s/designer/2/owned/and",
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/wanttobuy",
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/wanttoplay",
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/preordered",
        "http://friendlessstats.dtdns.net/dynamic/image/lifetime/%s",
        "http://friendlessstats.dtdns.net/dynamic/image/morepie/%s/2014",
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/designer/7/designer/42/minus",
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/designer/125/designer/1727/or",
        "http://friendlessstats.dtdns.net/dynamic/favourites/%s/category/Abstract Strategy/owned/and",
        "http://friendlessstats.dtdns.net/dynamic/image/pogo/%s/all",
        "http://friendlessstats.dtdns.net/dynamic/image/pogo/%s/designer/4958",
        "http://friendlessstats.dtdns.net/dynamic/selections/%s/designer/2/designer/7/designer/125/designer/141/designer/770/",
        "http://friendlessstats.dtdns.net/dynamic/selections/%s/lpiy/2006/lpiy/2007/lpiy/2008/lpiy/2009/lpiy/2010/lpiy/2011/lpiy/2012/lpiy/2013/1 ",     
        "http://friendlessstats.dtdns.net/dynamic/selections/%s/designer/125/designer/2/designer/7/designer/244/designer/141/owned/map/and/5",
        "http://friendlessstats.dtdns.net/dynamic/selections/%s/designer/125/designer/2/designer/7/designer/244/designer/141/piy/2012/map/and/2",
        "http://friendlessstats.dtdns.net/dynamic/generic/%s/designer/2",
        "http://friendlessstats.dtdns.net/dynamic/calendar/%s/2012/stop/playCount/all/owned/minus",
        "http://friendlessstats.dtdns.net/dynamic/image/playrate/%s",
        "http://friendlessstats.dtdns.net/dynamic/image/playrateown/%s",
        "http://friendlessstats.dtdns.net/dynamic/playrate/%s",
        "http://friendlessstats.dtdns.net/dynamic/playrate/%s/prevowned",
        "http://friendlessstats.dtdns.net/dynamic/image/playrate/%s/fpiy/2014"
        ]
TAGS = ["pbpy", "obpy", "rbpy", "mmmpie", "pogo", "pogotable", "mostunplayed", "playrate", "playrateown", "playrateprev",
        "pbmever", "pbmytd", "pbmgraph", "pr", "pbq", "favourites", "fgbpy", "bestdays", "ratingByRanking", "unusual", "least",
        "shouldplay", "shouldplayown", "timeline", "thm", "thd", "thday", "dimesbydesigner", "florence" ]
CHOOSE_URL = "http://friendlessstats.dtdns.net/dynamic/choose/%s/%s"
GENERAL = [
    "http://friendlessstats.dtdns.net/dynamic/cookies/",  
    "http://friendlessstats.dtdns.net/dynamic/server/",
    "http://friendlessstats.dtdns.net/dynamic/meta/",
    "http://friendlessstats.dtdns.net/stats/rankings.html",
    "http://friendlessstats.dtdns.net/dynamic/index.html",
    "http://friendlessstats.dtdns.net/dynamic/australia.html",
    "http://friendlessstats.dtdns.net/dynamic/rankings/"
    ]
        
import urllib, time
errors = []
all = GENERAL[:]
for user in USERS:
    for url in URLS:
        all.append(url % user)
    for tag in TAGS:
        all.append(CHOOSE_URL % (user, tag))
for s in all:
    start = time.time()
    print s,
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
print "Site is %d%% working!" % ((len(all) - len(errors)) * 100 / len(all))
