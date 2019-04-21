import time, library

END_YEAR = time.localtime()[0]
END_MONTH = time.localtime()[1]
NEW_PLAYED_URL = "https://boardgamegeek.com/xmlapi2/plays?username=%s&mindate=%d-%d-01&maxdate=%d-%d-31&subtype=boardgame"
DAY = library.DAY

class Play:
    def __init__(self, game, expansions, date, count, raters, totalRatings, location):
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
            return "Played %s %d times on %s" % (self.game.name, self.count, self.date)
        else:
            return "Played %s with %s %d times on %s" % (self.game.name, " ".join([exp.name for exp in self.expansions]), self.count, self.date)

    def __cmp__(self, other):
        c = cmp(self.hashcode, other.hashcode)
        if c == 0:
            c = cmp(self.game.name, other.game.name)
        if c == 0:
            c = cmp(self.count, other.count)
        return c

    def toMap(self):
        return { "game" : self.game.name, "gameid" : self.game.bggid, "count" : self.count, "location" : self.location,
                 "date" : str(self.date), "year" : self.year, "month" : self.month, "day" : self.day,
                 "expansions" : [e.name for e in self.expansions], "expansionIds" : [e.bggid for e in self.expansions] }

    def allGames(self):
        return [ self.game ] + self.expansions

    def __hash__(self):
        return self.hashcode

def processPlaysFile(filename, recorded):
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
        recorded.add(date, (gameId, quantity, raters, ratingsTotal,  location, playerRecs))
    return numEntries

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
        count += 1
        total += r
    return (count, int(total))

