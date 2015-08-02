#! /usr/bin/env python
import sys, os
sys.path.append(".")

USERS = [ "Friendless", "sa266", "spellenclub ST", "PzVIE", "Damjon", "yzemaze" ]
URLS = [ 
        "%sdynamic/result/%s",
        "%sdynamic/tabbed/%s/1",
        "%sdynamic/tabbed/%s/2",
        "%sdynamic/tabbed/%s/3",
        "%sdynamic/tabbed/%s/4",
        "%sdynamic/tabbed/%s/5",        
        "%sdynamic/tabbed/%s/6",        
        "%sdynamic/image/pbq/%s",
        "%sdynamic/image/fpvr/%s",
        "%sdynamic/plays/%s/florence/lastyear",
        "%sdynamic/image/morgan/%s",
        "%sdynamic/image/pogo/%s",
        "%sdynamic/crazy/%s",
        "%sdynamic/numplayers/%s",
        "%sdynamic/series/%s",
        "%sdynamic/cat/%s/designer",
        "%sdynamic/cat/%s/mechanic",
        "%sdynamic/cat/%s/category",
        "%sdynamic/image/lag/%s",
        "%sdynamic/unusual/%s",
        "%sdynamic/checklist/%s",
        "%sdynamic/multiyear/%s",
        "%sdynamic/locations/%s",
        "%sdynamic/plays/%s/totals",
        "%sdynamic/yearcomparison/%s",
        "%sdynamic/updates/%s",
        "%sdynamic/year/%s/2012",
        "%sdynamic/trade/%s",
        "%sdynamic/image/newPlays/%s",
        "%sdynamic/favourites/%s",
        "%sdynamic/image/pbm/%s",
        "%sdynamic/playscsv/%s",
        "%sdynamic/multiyear/%s",
        "%sdynamic/ipod/%s",
        "%sdynamic/image/lbr/%s",
        "%sdynamic/dimesbydesigner/%s",
        # want in trade or on wishlist
        "%sdynamic/favourites/%s/want/wishlist/1234/or",
        # All Peter Hawes games
        "%sdynamic/favourites/%s/designer/770",        
        # All games on your wishlist
        "%sdynamic/favourites/%s/wishlist/12345",        
        # Owned Knizia games
        "%sdynamic/favourites/%s/designer/2/owned/and",
        # Kramer without Kiesling
        "%sdynamic/favourites/%s/designer/7/designer/42/minus",
        # Either of the Brunos
        "%sdynamic/favourites/%s/designer/125/designer/1727/or",
        # previously owned modular board mechanic
        "%sdynamic/favourites/%s/mechanic/Modular Board/prevowned/and",
        # adventure category
        "%sdynamic/favourites/%s/category/Adventure",
        # plays of owned Knizias
        "%sdynamic/image/pogo/%s/designer/2/owned/and",
        "%sdynamic/favourites/%s/wanttobuy",
        "%sdynamic/favourites/%s/wanttoplay",
        "%sdynamic/favourites/%s/preordered",
        "%sdynamic/image/lifetime/%s",
        "%sdynamic/image/morepie/%s/2014",
        "%sdynamic/favourites/%s/designer/7/designer/42/minus",
        "%sdynamic/favourites/%s/designer/125/designer/1727/or",
        "%sdynamic/favourites/%s/category/Abstract Strategy/owned/and",
        "%sdynamic/image/pogo/%s/all",
        "%sdynamic/image/pogo/%s/designer/4958",
        "%sdynamic/selections/%s/designer/2/designer/7/designer/125/designer/141/designer/770/",
        "%sdynamic/selections/%s/lpiy/2006/lpiy/2007/lpiy/2008/lpiy/2009/lpiy/2010/lpiy/2011/lpiy/2012/lpiy/2013/1 ",     
        "%sdynamic/selections/%s/designer/125/designer/2/designer/7/designer/244/designer/141/owned/map/and/5",
        "%sdynamic/selections/%s/designer/125/designer/2/designer/7/designer/244/designer/141/piy/2012/map/and/2",
        "%sdynamic/generic/%s/designer/2",
        "%sdynamic/calendar/%s/2012/stop/playCount/all/owned/minus",
        "%sdynamic/image/playrate/%s",
        "%sdynamic/image/playrateown/%s",
        "%sdynamic/playrate/%s",
        "%sdynamic/playrate/%s/prevowned",
        "%sdynamic/image/playrate/%s/fpiy/2014"
        ]
TAGS = ["pbpy", "obpy", "rbpy", "mmmpie", "pogo", "pogotable", "mostunplayed", "playrate", "playrateown", "playrateprev",
        "pbmever", "pbmytd", "pbmgraph", "pr", "pbq", "favourites", "fgbpy", "bestdays", "ratingByRanking", "unusual", "least",
        "shouldplay", "shouldplayown", "timeline", "thm", "thd", "thday", "dimesbydesigner", "florence", "streaks" ]
CHOOSE_URL = "%sdynamic/choose/%s/%s"
GENERAL = [
    "%sdynamic/cookies/",  
    "%sdynamic/server/",
    "%sdynamic/meta/",
    "%sstats/rankings.html",
    "%sdynamic/index.html",
    "%sdynamic/australia.html",
    "%sdynamic/rankings/"
    ]
        
import urllib, time, sitedata
errors = []
all = [ g % sitedata.site for g in GENERAL ]
for user in USERS:
    for url in URLS:
        all.append(url % (sitedata.site, user))
    for tag in TAGS:
        all.append(CHOOSE_URL % (sitedata.site, user, tag))
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
