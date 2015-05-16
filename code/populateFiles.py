#!/usr/bin/env python

import MySQLdb, sys, time, _mysql_exceptions, time, os, urllib, pickle, xml.dom.minidom, socket
import mydb, sitedata, library
from geek import NoSuchGame

COLLECTION_URL = u"http://boardgamegeek.com/xmlapi2/collection?username=%s&brief=1&stats=1"
PLAYED_URL = "http://boardgamegeek.com/plays/bymonth/user/%s/subtype/boardgame"
PROFILE_URL = "http://boardgamegeek.com/user/%s"
TOP50_URL = "http://www.boardgamegeek.com/browse/boardgame"
MOST_VOTERS_URL = "http://boardgamegeek.com/browse/boardgame?sort=numvoters&sortdir=desc"
GAME_URL = "http://boardgamegeek.com/xmlapi/boardgame/%d&stats=1"
MARKET_URL = "http://www.boardgamegeek.com/geekstore.php3?action=viewuser&username=%s"

def readUserNames():
    uf = open(sitedata.cfgdir + "usernames.txt")
    usernames = [ line.strip() for line in uf.readlines() ]
    uf.close()
    usernames = [ u for u in usernames if len(u) > 0 ]
    return usernames

def readGameIds():
    result = mydb.query("select bggid from games")
    ret = [x[0] for x in result]
    return ret

def processPlayed(filename, geek, url):     
    import calendar, plays, datetime, stat
    db = mydb.get()
    existing = library.dbexec(db, "select count(*) from monthsplayed where geek = '%s'" % geek)
    noneBefore = existing[0][0] == 0l
    toAdd = []
    for line in file(filename).readlines():
        if line.find(">By date<") >= 0:
            s = library.between(line, '/end/', '"')
            fields = s.split("-")
            data = [geek, fields[1], fields[0]]
            toAdd.append(data)   
    if len(toAdd) > 0:
        ensureGeek(geek)
        library.dbexec(db, "delete from monthsplayed where geek = '%s'" % geek)
        luData = {}
        lastUpdateTimes = library.dbexec(db, "select url, lastupdate from files where geek = '%s' and processMethod = 'processPlays'" % geek)
        for (url, lu) in lastUpdateTimes:
            luData[url] = lu
        library.dbexec(db, "delete from files where geek = '%s' and processMethod = 'processPlays'" % geek)
        for data in toAdd:
            m = int(data[1])
            y = int(data[2])
            library.dbexec(db, "insert into monthsplayed (geek, month, year) values ('%s', %s, %s)" % tuple(data))
            playsFile = "played_%s_%02d_%d.xml" % (geek, m, y)
            url = plays.NEW_PLAYED_URL % (urllib.quote(geek), y, m, y, m)
            if m == 0 and y == 0:
                daysSince = 10000
                url = "http://boardgamegeek.com/xmlapi2/plays?username=%s&mindate=0000-00-00&maxdate=0000-00-00&subtype=boardgame" % urllib.quote(geek)
            else:
                try:
                    pd = datetime.date(y, m, calendar.monthrange(y,m)[1])
                except calendar.IllegalMonthError:
                    print "IllegalMonthError", y, m, data                
                daysSince = (library.TODAY - pd).days
            if daysSince <= 3: 
                tillNext = '24:00:00'
            elif daysSince <= 30:
                tillNext = '72:00:00'
            elif daysSince <= 60:
                tillNext = '168:00:00'
            else:
                tillNext = None
            description = "Plays for %d/%s" % (y,m)
            lu = luData.get(url)
            if tillNext is not None:
                if lu is not None:
                    mtime = lu.strftime('%Y-%m-%d %H:%M:%S')
                    sql2 = "insert into files (filename, url, processMethod, geek, lastupdate, tillNextUpdate, description) values ('%s', '%s', 'processPlays', '%s', '%s', '%s', '%s')" % (playsFile, url, geek, mtime, tillNext, description)
                else:
                    sql2 = "insert into files (filename, url, processMethod, geek, tillNextUpdate, description) values ('%s', '%s', 'processPlays', '%s', '%s', '%s')" % (playsFile, url, geek, tillNext, description)
            else:
                # no automatic next update - manual only
                if lu is not None:
                    mtime = lu.strftime('%Y-%m-%d %H:%M:%S')
                    sql2 = "insert into files (filename, url, processMethod, geek, lastupdate, description) values ('% s', '%s', 'processPlays', '%s', '%s', '%s')" % (playsFile, url, geek, mtime, description)
                else:
                    sql2 = "insert into files (filename, url, processMethod, geek, description) values ('%s', '%s', 'processPlays', '%s', '%s')" % (playsFile, url, geek, description)
            library.dbexec(db, sql2)                
        sql3 = "update files set nextUpdate = addtime(lastUpdate, tillNextUpdate) where processMethod = 'processPlays' and geek = '%s'" % geek
        library.dbexec(db, sql3)
        sql4 = "delete from plays where geek = '%s' and date_format(playDate, '%%Y-%%m') not in (select distinct concat(right(concat('000',year), 4), '-', right(concat('0',month), 2)) from monthsplayed where geek = '%s')" % (geek, geek)
        library.dbexec(db, sql4)
        db.close()
        return 1
    elif noneBefore:
        return 1
    else:
        print "nothing to add, check %s" % filename
        return 1
    
def processPlays(filename, geek, url):
    import datetime, calendar, mydb, plays, stat
    library.deleteFileIfBad(filename)
    try:
        ps = library.DictOfLists()
        mtime = os.stat(filename)[stat.ST_MTIME]
        fields = filename.split(".")[-2].split("_")
        month = int(fields[-2])
        year = int(fields[-1])
        startDate = None
        endDate = None
        try:
            startDate = datetime.datetime(year, month, 1)
            endDate = datetime.datetime(year, month, calendar.monthrange(year, month)[1], 23)
        except ValueError:
            if year != 0 or month != 0:
                print "That's a bad date", year, month
                return 1
        try:
            numEntries = plays.processPlaysFile(filename, ps)
            soFar = 100
            page = 2
            while soFar < numEntries:
                print "--- more entries from", filename, geek, url, soFar, numEntries, page
                filename2 = filename[:-4] + "_page%d.xml" % page
                url2 = url + "&page=%d" % page
                r = library.getFile(url2, filename2)
                if r == 0:
                    print "Failed to download page %d of %s." % (page, url)
                    return 0                
                plays.processPlaysFile(filename2, ps)
                page = page + 1
                soFar = soFar + 100
        except socket.error:
            import traceback
            traceback.print_exc()
            return 0
        print "Processing plays from %s" % filename
        db = mydb.get()
        if startDate is not None:        
            sql = "delete from plays where geek = %s and playDate between %s and %s"
            library.dbexec(db, sql, [geek, startDate, endDate])
        else:
            sql = "delete from plays where geek = %s and playDate = '0000-00-00'"
            library.dbexec(db, sql, [geek])
        sql = "delete from opponents where month = %s and year = %s and geek = %s"
        library.dbexec(db, sql, [month, year, geek])
        playerRecs = []
        for (date, dps) in ps.items():
            fields = date.split("-")
            try:
                (y, m, d) = (int(fields[0]), int(fields[1]), int(fields[2]))
            except ValueError:
                print "Invalid date", date
                import sys
                sys.exit(0)
            if m != month or y != year:
                print "Skipping Aldie's bug: games played in %d-%02d listed under entry for %d-%02d" % (y, m, year, month)
                continue
            if y == 0 and m == 0:
                d = '0000-00-00'
            else:
                d = datetime.date(y, m, d)
            playerRecs = playerRecs + _writePlaysToDB(db, geek, date, dps, d, month, year)
        _writeOpponentsToDB(db, geek, playerRecs, month, year)
        import frontpage
        frontpage.updateFrontPageData(geek)
        return 1
    except OSError:
        print "Couldn't find", filename
        return 0
    
class PlayerRecKey(object):
    def __init__(self, username, name, colour):
        self.username = username
        self.name = name
        self.colour = colour
        self.hash = hash(self.username) * 1000000 + hash(self.name) * 1000 + hash(self.colour)
    
    def __eq__(self, other):
        return self.username == other.username and self.name == other.name and self.colour == other.colour
    
    def __hash__(self):
        return self.hash
        
    def __str__(self):
        return str((self.username, self.name, self.colour))    
        
def _writePlaysToDB(db, geek, date, dps, d, month, year):
    import library, plays
    sql = "insert into plays (game, geek, playDate, quantity, basegame, raters, ratingstotal, location) values (%s, %s, %s, %s, %s, %s, %s, %s)"
    (processedPlays, playerRecs) = plays.createPlays(date, dps)
    for pp in processedPlays: 
        values = [pp.game.id, geek, d, pp.count, 0, pp.raters, pp.ratingsTotal,  pp.location]
        library.dbexec(db, sql, values)
        for eg in pp.expansions:
            values = [eg.id, geek, d, pp.count, pp.game.id, 0, 0]
            library.dbexec(db, sql, values)
    return playerRecs
            
def _writeOpponentsToDB(db, geek, playerRecs, month, year):         
    sql = "insert into opponents %s values %s"
    counts = library.Counts()
    for (username, name, colour) in playerRecs:
        if username == geek:
            continue
        counts.add(PlayerRecKey(username, name, colour))
    for (prk, count) in counts.items():
        if count < 2:
            continue
        lhs = []
        rhs = []
        binds = []
        if prk.name is not None:
            lhs.append("name")
            rhs.append("%s")
            binds.append(prk.name)
        if prk.username is not None:
            lhs.append("username")
            rhs.append("%s")
            binds.append(prk.username)
        if prk.colour is not None:
            lhs.append("colour")
            rhs.append("%s")
            binds.append(prk.colour)
        lhs = lhs + ["geek", "month", "year", "count"]
        rhs = rhs + ["%s", "%s", "%s", "%s"]
        binds = binds + [geek, month, year, count]
        l = "(" + ", ".join(lhs) + ")"
        r = "(" + ", ".join(rhs) + ")"
        s = sql % (l, r)
        library.dbexec(db, s, binds)

def processCollection(filename, geek, url):
    try:
        dom = xml.dom.minidom.parse(filename)
    except xml.parsers.expat.ExpatError, e:
        print "Error parsing XML in file %s" % filename, e
        return 0
    if len(dom.getElementsByTagName("items")) == 0:
        print "no items in %s" % filename
        return 0
    mydb.update("delete from geekgames where geek = '%s'" % geek)
    try:
        numpages = int(dom.getElementsByTagName("items")[0].getAttribute("numpages"))
    except ValueError:
        addGamesFromFile(filename, geek)
        import frontpage
        frontpage.updateFrontPageData(geek)        
        return 1
    for pn in range(numpages):
        p = str(pn+1)
        url = COLLECTION_URL % geek + "&page=" + p
        dest = sitedata.dbdir + "collection_%s_page%s.xml" % (geek, p)
        r = library.getFile(url, dest)
        if r == 0:
            return 0
        fixAmpersandsInXml(dest)
        addGamesFromFile(dest, geek)
    import frontpage
    frontpage.updateFrontPageData(geek)        
    return 1
    
def processMarket(filename, geek, url):
    import library
    data = []
    f = file(filename)  
    for line in f.readlines():
        if line.find("<div class='storeheader'>") >= 0:
            gameid = library.between(line, '/game/', '"')
        elif line.find("More Info...") >= 0:
            itemid = library.between(line, 'itemid=', '"')
            if itemid and gameid:
                data.append((geek, gameid, itemid))
    sql = "delete from market where geek = %s"
    mydb.update(sql, [geek])
    for (geek, gameid, itemid) in data:
        sql = "insert into market (geek, gameid, itemid) values (%s, %s, %s)"
        mydb.update(sql, [geek, gameid, itemid])
    return 1    
    
def processUser(filename, geek, url):
    f = file(filename)
    changes = 0
    sql = "select count(*) from users where geek = %s"
    data = mydb.query(sql, [geek])
    if int(data[0][0]) == 0:
        sql = "insert into users (geek) values (%s)"
        mydb.update(sql, [geek])
    for line in f.readlines():
        if line.find("/images/user/") > 0:
            n = int(library.between(line, "/images/user/", "/"))
            sql = "update users set bggid = %s where geek = %s"
            mydb.update(sql, [n, geek])  
            changes = changes + 1
        if line.find("/users?country=") > 0:
            s = library.between(line, "country=", '"')
            sql = "update users set country = %s where geek = %s"
            print "%s is in %s" % (geek, s)
            if s == "Australia":
                filename = "market_%s.html" % geek
                recordFile(mydb.get(), filename, MARKET_URL % geek, "processMarket", geek, "User marketplace data")
            mydb.update(sql, [s, geek])  
            changes = changes + 1  
        if changes == 2:
            break
    f.close()
    return changes

def addGamesFromFile(filename, geek):
    owned = {}
    try:
        dom = xml.dom.minidom.parse(filename)
    except xml.parsers.expat.ExpatError, e:
        print "Error parsing XML in file %s" % filename, e
        return 0
    if len(dom.getElementsByTagName("items")) == 0:
        return 0
    games = dom.getElementsByTagName("items")[0]
    gameNodes = games.getElementsByTagName("item")
    for gameNode in gameNodes:
        statusNode = gameNode.getElementsByTagName("status")[0]
        statsNode = gameNode.getElementsByTagName("stats")[0]
        try:
            g = int(gameNode.getAttribute("objectid"))
        except AttributeError:
            continue
        if owned.get(g) is not None:
            game = owned[g]
        else:
            game = library.Row()
            game.game = g
            game.owned = False
            game.prevowned = False
            game.wanttobuy = False
            game.wanttoplay = False
            game.preordered = False
            game.rating = -1
        game.owned = game.owned or int(statusNode.getAttribute("own"))
        game.prevowned = game.prevowned or int(statusNode.getAttribute("prevowned"))
        game.wanttobuy = game.wanttobuy or int(statusNode.getAttribute("wanttobuy"))
        game.wanttoplay = game.wanttoplay or int(statusNode.getAttribute("wanttoplay"))
        game.preordered = game.preordered or int(statusNode.getAttribute("preordered"))
        game.geek = geek
        try:
            ratingNode = statsNode.getElementsByTagName("rating")[0]
            game.rating = max(float(ratingNode.getAttribute("value")), game.rating)
        except ValueError:
            game.rating = -1.0
        if game.rating == 0.0:
            game.rating = -1.0
        comments = gameNode.getElementsByTagName("comment")
        if len(comments) > 0:
            game.comment = getText(comments[0])
        else:
            game.comment = "&nbsp;"
        if len(game.comment) > 1024:
            game.comment = game.comment[:1024]
        game.wish = statusNode.getAttribute("wishlistpriority")
        if game.wish == "":
            game.wish = "0"
        game.want = statusNode.getAttribute("want")
        if game.want == "":
            game.want = "0"
        game.trade = statusNode.getAttribute("fortrade")
        if game.trade == "":
            game.trade = "0"
        if game.owned:
            owned[game.game] = game
        ensureGame(game.game)
        db = mydb.get()
        existingRating = getExistingRating(db, geek, game.game)
        if existingRating is not None and existingRating > game.rating:
            game.rating = existingRating
        library.saveRow(db, game, "geekgames", "geek = '%s' and game = %d" % (geek, game.game))
        db.close()
        mydb.update("delete from geekgametags where geek = '%s'" % geek)
        try:
            tagsNode = gameNode.getElementsByTagName("tags")[0]
            tagNodes = gameNode.getElementsByTagName("tag")
            db = mydb.get()
            for tagNode in tagNodes:
                tag = library.Row()
                tag.geek = geek
                tag.game = game.game
                tag.tag = getText(tagNode).encode('utf8')
                print tag.geek, tag.game, tag.tag
                if tag.tag.startswith("own:"):
                    continue
                library.saveRow(db, tag, "geekgametags", "geek = '%s' and game = %d" % (tag.geek, tag.game))
            db.close()
        except IndexError:
            # no tags
            pass

def getExistingRating(db, geek, bggid):
    sql = "select rating from geekgames where geek = '%s' and game = %d" % (geek, bggid)
    data = mydb.query(sql)
    if len(data) > 0 and len(data[0]) > 0:
        return data[0][0]
    return None

def getNodeText(node):
    rc = ""
    for node in node.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
            print 347, node.data
    return rc

def _readFile(game, id, filename):
    import library
    game.expands = []
    try:
        dom = xml.dom.minidom.parse(filename)
    except xml.parsers.expat.ExpatError:
        if library.deleteFileIfBad(filename):
            print "Unable to parse %s" % filename
            import traceback
            traceback.print_exc()
        return None
    except IOError:
        print "File %s is bad" % filename
        return None
    gameNode = dom.getElementsByTagName("boardgames")
    if gameNode is None or gameNode == []:
        print "No game in file %s" % filename
        raise NoSuchGame(filename)
    try:
        names = dom.getElementsByTagName("name")
        if names is None or names == []:
            print "No such game as %s" % str(id)
            raise NoSuchGame(filename)
        for n in names:
            if str(n.getAttribute("primary")) == "true":
                game.name = library.getText(n)
    except IndexError: 
        raise NoSuchGame(filename)
    try:
        thumbnail = dom.getElementsByTagName("thumbnail")[0]
        game.thumbnail = getNodeText(thumbnail)
    except IndexError: 
        game.thumbnail = ''
    try:
        expansions = dom.getElementsByTagName("boardgameexpansion")
        if expansions is not None and expansions != []:
            for exp in expansions:
                inbound = exp.getAttribute("inbound")
                if "true" == inbound:
                    expid = int(exp.getAttribute("objectid"))
                    game.expands.append(expid)
    except:
        game.expands = None
    try:
        stats = dom.getElementsByTagName("statistics")[0]
    except IndexError:
        print "No stats found in file %s" % filename
        stats = None
    if stats:
        try:
            ratings = stats.getElementsByTagName("ratings")[0]
        except IndexError:
            print "No ratings found in file %s" % filename
            ratings = None
        try:
            ranks = stats.getElementsByTagName("rank")
        except IndexError:
            print "No ranks found in file %s" % filename
            ranks = None
    else:
        ratings = None
        ranks = None
    if ranks:
        game.rank = -1
        game.subdomain = "boardgame"
        for e in ranks:
            if e.getAttribute("type") == "subtype" and e.getAttribute("name") == "boardgame":
                try:
                    game.rank = int(e.getAttribute("value"))
                except ValueError:
                    game.rank = -1
            elif e.getAttribute("type") == "family":
                game.subdomain = e.getAttribute("name")
                    
    else:
        game.rank = -1
    if ratings:
        try:
            game.average = float(library.getText(ratings.getElementsByTagName("average")[0]))
        except ValueError:
            # no ratings
            game.average = 0
        except IndexError:
            game.average = -1
        try:
            game.usersRated = int(library.getText(ratings.getElementsByTagName("usersrated")[0]))
        except ValueError:
            #self.usersRated = 0
            pass
        try:
            game.usersOwned = int(library.getText(ratings.getElementsByTagName("owned")[0]))
        except ValueError:
            #self.usersOwned = 0
            pass
        try:
            game.averageWeight = float(library.getText(ratings.getElementsByTagName("averageweight")[0]))
        except ValueError:
            game.averageWeight = 0
        except IndexError:
            game.averageWeight = 0
        try:
            game.bayesAverage = float(library.getText(ratings.getElementsByTagName("bayesaverage")[0]))
        except IndexError:
            game.bayesAverage = -1  
        except ValueError:
            game.bayesAverage = -1       
    else:
        game.average = 5.5
        game.averageWeight = 0
        game.bayesAverage = 5.5   
    game.categories = library.getTextList(dom.getElementsByTagName("boardgamecategory"))
    try:
        yptags = dom.getElementsByTagName("yearpublished")
        game.year = int(library.getText(yptags[0]))
    except ValueError:
        game.year = 0
    except IndexError:
        game.year = 0
    try:
        game.minPlayers = int(library.getText(dom.getElementsByTagName("minplayers")[0]))
    except ValueError:
        game.minPlayers = 0
    try:
        game.maxPlayers = int(library.getText(dom.getElementsByTagName("maxplayers")[0]))
    except ValueError:
        game.maxPlayers = 0
    game.designers = library.getRawIDList(dom.getElementsByTagName("boardgamedesigner"), "objectid")
    if len(game.designers) == 0:
        game.designers = [ (-1, "Unknown") ]
    game.publishers = library.getRawIDList(dom.getElementsByTagName("boardgamepublisher"), "objectid")
    try:
        game.playTime = int(library.getText(dom.getElementsByTagName("playingtime")[0]))
    except ValueError:
        game.playTime = 0
    game.mechanics = library.getTextList(dom.getElementsByTagName("boardgamemechanic"))
    _addNumPlayersData(game, dom)
    return game
    
def _addNumPlayersData(game, dom):
    polls = dom.getElementsByTagName("poll")
    game.numPlayers = {}
    for poll in polls:
        if poll.getAttribute("name") == "suggested_numplayers":
            results = poll.getElementsByTagName("results")
            for rs in results:
                plus = False
                n = rs.getAttribute("numplayers")
                if n == "+":
                    # test data can say this
                    continue
                elif n.endswith("+"):
                    n = int(n[:-1]) + 1
                    plus = True
                else:
                    n = int(n)
                if n >= 8:
                    continue
                result = rs.getElementsByTagName("result")
                for r in result:
                    key = r.getAttribute("value")
                    if key == "Best":
                        key = "best"
                    elif key.startswith("R"):
                        key = "recommended"
                    elif key.startswith("N"):
                        key = "notrec"
                    v = int(r.getAttribute("numvotes"))
                    game.numPlayers[key + `n`] = v
                    if plus:
                        m = n
                        while m < 7:
                            m = m + 1
                            game.numPlayers[key + `m`] = v

def saveNumPlayers(id, numPlayers):
    if len(numPlayers) == 0:
        return
    numPlayers["game"] = id
    mydb.saveRow(numPlayers, "numplayers", "game = %d" % id)
    
def saveGameExpands(id, bases):
    mydb.update("delete from expansions where expansion = %d" % id)
    for b in bases:
        mydb.update("insert into expansions (basegame, expansion) values (%s, %d)" % (b, id))

def _saveToDatabase(game):
    for (did, dname) in game.designers:
        ensureDesigner(did, dname)
    for (pid, pname) in game.publishers:
        ensurePublisher(pid, pname)
    ensureGame(game.id)
    saveGameDesigners(game.id, [ d[0] for d in game.designers ])
    saveGamePublishers(game.id, [ p[0] for p in game.publishers ])
    saveGameCategories(game.id, game.categories)
    saveGameMechanics(game.id, game.mechanics)
    saveNumPlayers(game.id, game.numPlayers)
    saveGameData(game)
    if game.expands is not None:
        saveGameExpands(game.id, game.expands)    

def processGame(filename, geek, url):
    game = library.Thing()
    game.subdomain = "boardgame"
    if "/" not in filename:
        filename = sitedata.dbdir + filename
    id = int(library.between(filename[filename.rfind('/'):], "/", "."))
    game.id = id
    if _readFile(game, id, filename) is None:
        return 0
    if game.rank > 0:
        sql = "update files set tillNextUpdate = '360:00:00' where filename = %s"
        mydb.update(sql, [filename])
    _saveToDatabase(game)
    return 1

def refreshFile(filename, url, method, geek):
    global theNumbers
    if url:
        print "%s Processing %s %s" % (time.strftime("%H:%M:%S"), filename, `theNumbers`)
        dest = sitedata.dbdir + filename
        try:
            r = library.getFile(url, dest)
        except IOError:
            print "IOError"
            return 0
        if r == 0:
            return 0
    else:
        dest = None
    import os
    if dest is not None and not os.access(dest, os.R_OK):
        print dest, "inaccessible"
        return 0
    result = eval("%s('%s', '%s', '%s')" % (method, dest, geek, url), globals(), locals())
    if result and (dest is not None):
        try:
            os.remove(dest)
        except OSError:
            pass
    return result

def updateFiles(records, index, finish):
    import time
    global theNumbers
    for record in records:
        if finish is not None and time.time() > finish:
            break
        try:
            sql = "update files set lastattempt = now() where url = %s"
            mydb.update(sql, [record[1]])
            if refreshFile(record[0], record[1], record[2], record[3]):
                sql = "update files set lastUpdate = now() where url = '%s'" % record[1]
                mydb.update(sql)
                sql = "update files set nextUpdate = addtime(lastUpdate, tillNextUpdate) where url = '%s'" % record[1]
                mydb.update(sql)
            else:
                print "DIDN'T PROCESS %s" % record[1]
        except NoSuchGame:
            sql = "delete from files where url = '%s'" % record[1]
            mydb.update(sql)
        theNumbers[index] = theNumbers[index] - 1
            
theNumbers = None            

def refreshFiles(nullOnly, finishTime):
    global theNumbers
    sql = "select filename, url, processMethod, geek from files where lastUpdate is null order by lastattempt"
    files1 = mydb.query(sql)
    sql = "select filename, url, processMethod, geek from files where nextUpdate < now() and processMethod != 'processGame' order by lastattempt"
    files2 = mydb.query(sql)
    sql = "select filename, url, processMethod, geek from files where nextUpdate < now() and processMethod = 'processGame' order by lastattempt"
    files3 = mydb.query(sql)
    reserveFor3 = 30
    reserveFor2 = 30
    if len(files2) == 0:
        reserveFor2 = 0
    if len(files3) == 0:
        reserveFor3 = 0
    theNumbers = [len(files1), len(files2), len(files3)]
    updateFiles(files1, 0, finishTime - reserveFor3 - reserveFor2)
    if nullOnly:
        return
    updateFiles(files2, 1, finishTime - reserveFor3)
    updateFiles(files3, 2, finishTime)

def ts(t):
    s = time.localtime(t)
    return MySQLdb.Timestamp(s[0], s[1], s[2], s[3], s[4], s[5])

HIST_SQL = "insert into history (geek, ts, friendless, wanted, wished, owned, unplayed, distinctPlayed, traded, nickelPercent, yourAverage, percentPlayedEver, percentPlayedThisYear, averagePogo, bggAverage, curmudgeon, meanYear, the100, sdj, top50, totalPlays, medYear) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

def sqlQuote(s):
    return s.replace(u"'", u"''").encode("utf8")

def ensureGeek(geek):
    count = mydb.query("select count(*) from geeks where username = '%s'" % geek)[0][0]
    if count == 0l:
        mydb.update("insert into geeks (username) values ('%s')" % geek)

def ensureDesigner(id, name):
    count = mydb.query("select count(*) from designers where bggid = %d" % id)[0][0]
    if count == 0l:
        mydb.update("insert into designers (bggid, name, boring) values (%d, '%s', %d)" % (id, sqlQuote(name), name.startswith("(")))
    else:
        mydb.update("update designers set name = '%s', boring = %d where bggid = %d" % (sqlQuote(name), name.startswith("("), id))

def ensurePublisher(id, name):
    count = mydb.query("select count(*) from publishers where bggid = %d" % id)[0][0]
    if count == 0l:
        mydb.update("insert into publishers (bggid, name) values (%d, '%s')" % (id, sqlQuote(name)))
    else:
        mydb.update("update publishers set name = '%s' where bggid = %d" % (sqlQuote(name), id))

def saveGameDesigners(id, ds):
    mydb.update("delete from gameDesigners where gameId = %d" % id)
    for d in ds:
        mydb.update("insert into gameDesigners (gameId, designerId) values (%d, '%s')" % (id, d))

def saveGamePublishers(id, ps):
    mydb.update("delete from gamePublishers where gameId = %d" % id)
    for p in ps:
        mydb.update("insert into gamePublishers (gameId, publisherId) values (%d, '%s')" % (id, p))

def saveGameCategories(id, cats):
    mydb.update("delete from gameCategories where gameId = %d" % id)
    for cat in cats:
        mydb.update("insert into gameCategories (gameId, category) values (%d, '%s')" % (id, sqlQuote(cat)))

def saveGameMechanics(id, mecs):
    mydb.update("delete from gameMechanics where gameId = %d" % id)
    for mec in mecs:
        mydb.update("insert into gameMechanics (gameId, mechanic) values (%d, '%s')" % (id, sqlQuote(mec)))

def ensureGame(game,  recurseCheck=[]):
    count = mydb.query("select count(*) from games where bggid = %d" % game)[0][0]
    if count == 0l:
        mydb.update("insert into games (bggid) values (%d)" % game)
    basegames = getBaseGames(game)
    for g in basegames:
        if g not in basegames:
            ensureGame(g,  recurseCheck + basegames + [game])

def addGame(id):
    ensureGame(id)
    # main(True)

def saveGameData(game):
    if game.__dict__.get("usersRated") is None:
        s = "update games set name = '%s', subdomain = '%s', average = %f, rank = %d, yearPublished = %d, minPlayers = %d, maxPlayers = %d, playTime = %d, averageWeight = %f, bayesAverage = %f, thumbnail = '%s' where bggid = %d" %  \
            (sqlQuote(game.name), sqlQuote(game.subdomain), game.average, game.rank, game.year, game.minPlayers, game.maxPlayers, game.playTime, game.averageWeight, game.bayesAverage, sqlQuote(game.thumbnail), game.id)
        print s
        mydb.update(s)
    else:
        s = "update games set name = '%s', subdomain = '%s', average = %f, rank = %d, yearPublished = %d, minPlayers = %d, maxPlayers = %d, playTime = %d, averageWeight = %f, bayesAverage = %f, thumbnail = '%s', usersOwned = %d, usersRated = %d where bggid = %d" % \
            (sqlQuote(game.name), sqlQuote(game.subdomain), game.average, game.rank, game.year, game.minPlayers, game.maxPlayers, game.playTime, game.averageWeight, game.bayesAverage, sqlQuote(game.thumbnail), game.usersOwned, game.usersRated, game.id)
        mydb.update(s)

def ensureExpansion(base, expansion):
    ensureGame(base)
    ensureGame(expansion)
    count = mydb.query("select count(*) from expansions where basegame = %d and expansion = %d" % (base, expansion))[0][0]
    if count == 0l:
        mydb.update("insert into expansions (basegame, expansion) values (%d, %d)" % (base, expansion))
        
def getBaseGames(expansion):
    bgs = mydb.query("select basegame from expansions where expansion = %d" % expansion)
    return [ x[0] for x in bgs ]

def ensureSeries(series, game):
    ensureGame(game)
    count = mydb.query("select count(*) from series where game = %d and name = '%s'" % (game, series))[0][0]
    if count == 0l:
        mydb.update("insert into series (game, name) values (%d, '%s')" % (game, series))

def ensureRule(ruleType, gameId):
    mydb.update("insert into metadata (ruletype, bggid) values (%d, '%s')" % (ruleType, gameId))

# longest possible MySQL time is 838:59:59 hours: http://dev.mysql.com/doc/refman/5.5/en/date-and-time-type-overview.html
TILL_NEXT_UPDATE = { 'processCollection' : '72:00:00', 'processMarket' : '72:00:00', 'processPlayed' : '72:00:00',
    'processGame' : '838:00:00', 'processTop50' : '72:00:00', "processFrontPage" : '24:00:00' }

def recordFile(db, filename, url, processMethod, geek, description):
    # delete old URLs for the same file
    # sql = "delete from files where filename = '%s' and geek = '%s' and processMethod = '%s' and url != '%s'" % (filename, geek, processMethod, url)
    # dbexec(db, sql)
    if url is None:
        if geek is None:
            sql = "select count(*) from files where processMethod = '%s'" % processMethod
        else:
            sql = "select count(*) from files where processMethod = '%s' and geek = '%s'" % (processMethod, geek)
    else:
        sql = "select count(*) from files where url = '%s'" % url
    data = library.dbexec(db, sql)
    if len(data) == 0:
        print data
        print geek
        print url
        print processMethod
    count = data[0][0]
    if count == 0:
        till = TILL_NEXT_UPDATE.get(processMethod)        
        if filename is None:
            # if there is no file there should be no URL either
            sql2 = "insert into files (processMethod, geek, tillNextUpdate, description) values (%s, %s, %s, %s)"
            args = [processMethod, geek, till, description]
        else:
            try:
                import os, stat
                mtime = os.stat(sitedata.dbdir + filename)[stat.ST_MTIME]
                sql2 = "insert into files (filename, url, processMethod, geek, lastupdate, tillNextUpdate, description) values (%s, %s, %s, %s, FROM_UNIXTIME(%s), %s, %s)" 
                args = [filename, url, processMethod, geek, mtime, till, description]
            except OSError:
                sql2 = "insert into files (filename, url, processMethod, geek, tillNextUpdate, description) values (%s, %s, %s, %s, %s, %s)"
                args = [filename, url, processMethod, geek, till, description]
        library.dbexec(db, sql2, args)

def populateFiles():
    usernames = readUserNames()
    print "%d users" % len(usernames)
    db = mydb.get()
    for u in usernames:
        ensureGeek(u)
        uu = urllib.quote(u)
        filename = '%s_collection.xml' % u
        recordFile(db, filename, COLLECTION_URL % uu, "processCollection", u, "User collection - owned, ratings, etc")
        filename = "%s_played.html" % u
        recordFile(db, filename, PLAYED_URL % uu, "processPlayed", u, "Months in which user has played games")
        filename = "%s_profile.html" % u
        recordFile(db, filename, PROFILE_URL % uu, "processUser", u, "User's profile")
    bggids = readGameIds()
    print "%d games" % len(bggids)
    shouldDeleteGames = []
    for id in bggids:
        filename = "%d.xml" % id
        recordFile(db, filename, GAME_URL % id, "processGame", None, "Game " + str(id))
    recordFile(db, "top50.html", TOP50_URL, "processTop50", None, "Top 50")
    recordFile(db, "mostVoters.html", MOST_VOTERS_URL, "processMostVoters", None, "Most Voters")
    recordFile(db, None, None, "processFrontPage", None, "Front Page")
    sql = "update files set nextUpdate = addtime(lastUpdate, tillNextUpdate) where nextUpdate is null and url is not null"
    library.dbexec(db, sql)
    db.close()
    
def copyDynamicPageToStatic(destFilename, srcFilename):
    import urllib, sitedata
    dest = sitedata.resultdir + destFilename
    src = sitedata.site + srcFilename
    print "Save %s to %s" % (src, dest)
    try:
        urllib.urlretrieve(src, dest)
        return 1
    except IOError:
        import traceback
        traceback.print_exc()
        return 0    
    
def processFrontPage(filename, geek, url):  
    # the dynamic front page is expensive to generate so we download it and save a static copy
    import urllib, sitedata, socket
    socket.setdefaulttimeout(1200)
    result = 1
    result = result * copyDynamicPageToStatic("rankings.html", "dynamic/rankings/all")
    return result
    
def getExtendedTop100():
    sql = "select sum(rating), game from geekgames where rating > 0  and (game not in (select gameId from gameCategories where category = 'Expansion for Base-game' or category = 'Book')) group by game order by 1 desc limit 100"    
    data = mydb.query(sql)
    return [int(d[1]) for d in data]

def getTop50(filename):
    print filename
    t50 = []
    f = open(filename)
    start = False
    for line in f.readlines():
        line = line.strip()
        if not start and line.find("<th class='collection_bggrating'>") >= 0:
            start = True
        elif start and line.find('href="/boardgame/') >= 0:
            id = library.between(line, 'href="/boardgame/', '/')
            id = int(id)
            if id not in t50:
                t50.append(id)
            if len(t50) == 50:
                break
    f.close()
    return t50

def getMostVoters(filename):
    mv = []
    f = open(filename)
    start = False
    for line in f.readlines():
        line = line.strip()
        if not start and line.find("<th class='collection_bggrating'>") >= 0:
            start = True
        elif start and line.find('href="/boardgame/') >= 0:
            id = library.between(line, 'href="/boardgame/', '/')
            mv.append(int(id))
    f.close()
    return mv

def readMetadata():
    series = {}
    expansions = []
    f = file(sitedata.cfgdir + "metadata.txt")
    for line in f.readlines():
        line = line.strip()
        if line.find('#') >= 0:
            line = line[:line.find('#')].strip()
        if len(line) == 0:
            continue
        elif line.find(":") >= 0:
            key = line[:line.find(":")].strip()
            ids = line[line.find(":")+1:].split()
            ids = [ library.beforeSlash(s) for s in ids ]
            ids = [ int(s) for s in ids ]
            series[key] = ids
        else:
            expansions.append(line)
    f.close()
    return (series, expansions)
    
RULE_TYPES = { "expansion" : library.EXPANSION, "basegame" : library.BASEGAME }    

def processTop50(filename, geek, url):
    (series, expansions) = readMetadata()
    mydb.update("delete from metadata")
    for line in expansions:
        fields = line.split(" ")
        if len(fields) != 2 or RULE_TYPES.get(fields[0]) is None:
            print "WHAT'S", line
        else:
            type = RULE_TYPES.get(fields[0])
            gameId = int(fields[1])
            ensureRule(type, gameId)
    series["Top 50"] = getTop50(filename)
    if len(series["Top 50"]) == 0:
        # try again next time
        print "Could not retrieve top 50"
        return 0
    print "Top 50:", series["Top 50"]
    series["Extended Stats Top 100"] = getExtendedTop100()
    print "Extended Top 100:", series["Extended Stats Top 100"]
    for (series, games) in series.items():
        mydb.update("delete from series where name = '%s'" % series)
        for e in games:
            ensureSeries(series, e)
    print int(mydb.query("select count(*) from series")[0][0]), "games in series"
    return 1

def processMostVoters(filename, geek, url):
    mydb.update("delete from series where name = 'Most Voters'")
    mvs = getMostVoters(filename)
    if len(mvs) == 0:
        # try again next time
        print "Could not retrieve Most Voters"
        return 0
    print "Most Voters:", mvs
    for e in mvs:
        ensureSeries("Most Voters", e)
    return 1

def deleteUsers(users):
    db = mydb.get()
    library.dbexec(db, "delete from geekgametags where geek in (%s)" % users)
    library.dbexec(db, "delete from history where geek in (%s)" % users)
    library.dbexec(db, "delete from monthsplayed where geek in (%s)" % users)
    library.dbexec(db, "delete from geekgames where geek in (%s)" % users)
    library.dbexec(db, "delete from files where geek in (%s)" % users)
    library.dbexec(db, "delete from geeks where username in (%s)" % users)
    db.close()

def main(nullOnly, finish):
    #dbexec(db, "alter table games add column expansion int unsigned not null default 0")
    #dbexec(db, "update files set lastUpdate = null where processMethod = 'processTop50'")
    #dbexec(db, "delete from files where processMethod = 'processCollection' and url like '%all=1'")
    #dbexec(db, "delete from files")
    if not nullOnly:
        usernames = readUserNames()
        inlist = ", ".join([("'%s'" % u) for u in usernames])
        oldUsers = mydb.query("select username from geeks where username not in (%s)" % inlist)
        if len(oldUsers) > 0:
            deleteList = ", ".join([("'%s'" % u) for u in oldUsers])
            print "These users should be deleted:", deleteList
            deleteUsers(deleteList)
        populateFiles()
    refreshFiles(nullOnly, finish)

if __name__ == "__main__":
    import time
    main(False, time.time() + 300)
