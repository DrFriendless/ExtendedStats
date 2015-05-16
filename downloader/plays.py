import time, library, os, sitedata

END_YEAR = time.localtime()[0]
END_MONTH = time.localtime()[1]
NEW_PLAYED_URL = "http://boardgamegeek.com/xmlapi2/plays?username=%s&mindate=%d-%d-01&maxdate=%d-%d-31&subtype=boardgame"
DAY = library.DAY

class Play:
    def __init__(self, game, expansions, date, count, raters, totalRatings,  location):
        import datetime
        self.game = game
        self.expansions = expansions
        self.count = count
        self.raters = raters
        self.ratingsTotal = totalRatings
        self.location = location
        if self.location is None:
            self.location = ""
        elif len(self.location) > 32:
            self.location = self.location[:32]
        if type(date) == type("") or type(date) == type(u""):
            self.date = date
            fields = date.split("-")
            self.year = int(fields[0])
            self.month = int(fields[1])
            self.day = int(fields[2])
        else:
            # datetime
            try:
                (self.year, self.month, self.day) = (date.year, date.month, date.day)
            except AttributeError:
                (self.year, self.month, self.day) = (0, 0, 0)
            self.date = "%4d-%02d-%02d" % (self.year, self.month, self.day)
        if self.year == 0:
            self.dt = None
        else:
            self.dt = datetime.date(self.year, self.month, self.day)
        self.hashcode = self.year * 10000 + self.month * 100 + self.day
        
    def __repr__(self):
        if len(self.expansions) == 0:
            return "Played %s %d times on %s" % (`self.game`, self.count, self.date)
        else:
            return "Played %s with %s %d times on %s" % (`self.game`, " ".join([`exp` for exp in self.expansions]), self.count, self.date)

    def __cmp__(self, other):
        c = cmp(self.hashcode, other.hashcode)
        if c == 0:
            c = cmp(self.game, other.game)
        if c == 0:
            c = cmp(self.count, other.count)
        return c

    def allGames(self):
        return [ self.game ] + self.expansions

    def __hash__(self):
        return self.hashcode

def createPlays(db, date, ps):
    import populateFiles
    ps = [ (populateFiles.getGame(id, db), q, r, t, loc, playerRecs) for (id, q, r, t,  loc, playerRecs) in ps ]
    # filter out plays of games which don't exist
    ps = [ p for p in ps if p[0] is not None ]
    plays = []
    recs = []
    for (game, quantity, raters, ratingsTotal, location, playerRecs) in ps:
        try:
            plays.append(Play(game,  [],  date,  quantity,  raters,  ratingsTotal,  location))
            recs = recs + playerRecs
        except OverflowError:
            print "BAD DATE in play: %s" % str(date)
    return (plays, recs)

def processPlaysFile(db, geek, filename, recorded):
    import xml.dom.minidom
    try:
        dom = xml.dom.minidom.parse(filename)
    except xml.parsers.expat.ExpatError, e:
        print "Error parsing XML in file %s" % filename, e
        return
    playElements = dom.getElementsByTagName("play")
    if len(playElements) == 0:
        print "no plays in %s" % filename
        return
    try:
        numEntries = int(dom.getElementsByTagName("plays")[0].getAttribute("total"))
    except ValueError:
        numEntries = 1
    for pe in playElements:
        playerRecs = []
        date = pe.getAttribute("date")
        quantity = int(pe.getAttribute("quantity"))
        items = pe.getElementsByTagName("item")
        gameId = int(items[0].getAttribute("objectid"))
        location = pe.getAttribute("location")
        (raters, ratingsTotal) = getRatings(pe)
        playersNodes = pe.getElementsByTagName("players")
        if len(playersNodes):
            players = playersNodes[0].getElementsByTagName("player")
            for p in players:
                username = p.getAttribute("username")
                name = p.getAttribute("name")
                colour = p.getAttribute("color")
                if username == "":
                    username = None
                if name == "":
                    name = None
                if colour == "":
                    colour = None
                if username is not None or name is not None or colour is not None:
                    playerRecs.append((username, name, colour))
        if quantity < 10000:
            recorded.add(date, (gameId, quantity, raters, ratingsTotal,  location, playerRecs))
    return numEntries

def getAllPlays(db, geek):
    data = db.execute("select game, playDate, quantity from plays where geek = %s", [geek])
    return __reconstructPlays(geek, db, data)
    
def getRatings(pe):
    playersNodes = pe.getElementsByTagName("players")
    if len(playersNodes) == 0:
        return (0,0)
    playerNodes = playersNodes[0].getElementsByTagName("player")
    count = 0
    total = 0.0
    for pn in playerNodes:       
        r = float(pn.getAttribute("rating"))
        if r < 1 or r > 10:
            continue 
        count = count + 1
        total = total + r
    return (count, int(total))

def _inferExtraPlays(geek, db, plays):
    import library
    result = []
    playsByDate = library.DictOfLists()
    playCountByMonth = library.Counts()
    for play in plays:
        playsByDate.add(play.date, play)
        playCountByMonth.add(play.date[:7])
    for date in playsByDate.keys():
        debug = False
        datePs = playsByDate[date]
        if debug:
            print "before", datePs
        count = 0
        while True:
            (rs, changed) = _inferExtraPlaysForADate(debug, db, datePs)
            if not changed:
                break
            count = count + 1
            if count == 200:
                print "Got really confused", geek, date
                break
            datePs = rs
        if debug:
            print "after", rs
        result = result + rs
    return result
  
def _inferExtraPlaysForADate(debug, db, plays):
    import library
    result = []
    for play in plays:
        game = getGame(db, play.game)
        if game.expansion:
            for bgplay in plays:
                if play is bgplay:
                    continue
                bgplaygame = getGame(db, bgplay.game)
                if (bgplay.game in game.basegames or library.intersect(game.basegames, bgplaygame.expansions)) and play.game not in bgplay.expansions:                    
                    if debug: print "A"
                    nq = min(play.count, bgplay.count)
                    play.count = play.count - nq
                    bgplay.count = bgplay.count - nq
                    p = Play(bgplay.game, bgplay.expansions + [play.game] + play.expansions, bgplay.date, nq, bgplay.raters, bgplay.ratingsTotal,  "")
                    if debug:
                        print p
                    newps = [p]
                    if play.count > 0:
                        newps.append(play)
                    if bgplay.count > 0:
                        newps.append(bgplay)
                    orig = len(plays)
                    others = [ op for op in plays if op is not play and op is not bgplay ]
                    if len(others) == len(plays):
                        print "Failed to remove", plays, others                    
                    return (others + newps, True)
            # no known basegame
            if len(game.basegames) == 1:
                basegame = game.basegames[0]
                p = Play(basegame, [play.game] + play.expansions, play.date, play.count, play.raters, play.ratingsTotal,  "")
                others = [ op for op in plays if op is not play ]
                return (others + [p], True)
        result.append(play)
    return (result, False)    

def __reconstructPlays(geek, db, playsData):
    import plays
    ids = []
    for p in playsData:
        if p[0] not in ids:
            ids.append(p[0])
    getGames(db, ids)
    result = []
    for (id, ts, q) in playsData:           
        result.append(Play(id, [], ts, q, 0, 0, ""))
    result = _inferExtraPlays(geek, db, result)
    result.sort()
    return result  

games = {}

class Game(object):
    def __init__(self, id, name):
        self.id = id
        self.expansion = False
        self.name = name
        self.basegames = []
        self.expansions = []
        
def getGame(db, id):
    global games
    if games.get(id) is not None:
        return games[id]
    getGames(db, [id])
    return games[id]
        
def getGames(db, ids):
    if len(ids) == 0:
        return
    import library
    global games
    redo = True
    exdata = db.execute("select basegame, expansion from expansions where %s" % library.inlist("expansion", ids))
    while redo:
        redo = False
        for (bg, ex) in exdata:
            if bg not in ids:
                ids.append(bg)
                redo = True
    data = db.execute("select bggid from games where %s" % library.inlist("bggid", ids))
    for (bggid,) in data:
        games[bggid] = Game(bggid, None)
    for (bg, ex) in exdata:
        if games.get(bg) is None or games.get(ex) is None:
            continue
        games[ex].basegames.append(bg)
        games[bg].expansions.append(ex)
        games[ex].expansion = True