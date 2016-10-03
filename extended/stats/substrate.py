import math
LAMBDA = math.log(0.1) / -10.0
GAME_URL = "http://www.boardgamegeek.com/game/%d"

def optionKey(options):
    return "%s%s" % (str(options.excludeTrades), str(options.excludeExpansions))

class Substrate:
    """A wrapper around a geek to provide lookups common to the entire app."""

    def __init__(self, geek, context):
        self.geek = geek
        self.context = context
        # cache of loaded lists of geekgames
        self.collections = {}
        # cache of loaded games
        self.detailedGames = {}
        self.allPlays = None
        self.colls = None
        self.series = None

    def getGames(self, ids):
        """returns Game objects from the cache"""
        otherIds = []
        result = {}
        for id in ids:
            if self.detailedGames.get(id) is not None:
                result[id] = self.detailedGames[id]
            else:
                otherIds.append(id)
        moreGames = getGames(otherIds)
        self.detailedGames.update(moreGames)
        result.update(moreGames)
        if len(moreGames) < len(otherIds):
            pass
        return result

    def getGeekGames(self, ids):
        import library
        options = library.Thing()
        options.excludeExpansions = False
        options.excludeTrades = False
        all = self.getAllGeekGamesWithOptions(options)
        return [ gg for gg in all if gg.game.bggid in ids ]

    def __processGeekGames(self, geekgames):
        import library
        self.addPlaysDataToGeekGames(geekgames)
        for gg in geekgames:
            gg.utilisation = int(library.cdf(gg.plays, LAMBDA) * 1000.0) / 10.0

    def getTheseGeekGames(self, games):
        """returns GeekGame objects whether the user has a record for them or not"""
        import library
        opts = library.Thing()
        opts.excludeExpansions = False
        opts.excludeTrades = False
        allGames = self.getAllGeekGamesWithOptions(opts)
        result = [ gg for gg in allGames if gg.game in games ]
        done = [ gg.game for gg in result ]
        games = [ g for g in games if g not in done ]
        new = []
        for g in games:
            gg = createEmptyGeekGame(g)
            result.append(gg)
            new.append(gg)
        self.addPlaysDataToGeekGames(new)
        return result

    def getAllGeekGamesWithOptions(self,  options):
        """returns GeekGame objects"""
        import mydb, dbaccess
        key = optionKey(options)
        if self.collections.get(key) is not None:
            return self.collections[key]
        geekgames = dbaccess.getGeekGamesForGeek(self.geek)
        sql = "select distinct game from plays where geek = %s and game not in (select distinct game from geekgames where geek = %s)"
        playedData = [ d[0] for d in mydb.query(sql, [self.geek, self.geek]) ]
        playedGames = getGames(playedData)
        for bggid in playedGames.keys():
            gg = createEmptyGeekGame(playedGames[bggid])
            gg.game = bggid
            geekgames.append(gg)
        if options.excludeTrades:
            geekgames = [ gg for gg in geekgames if not gg.trade ]
        for gg in geekgames:
            gg.bggid = gg.game
        self.__processGeekGames(geekgames)
        games = self.getGames([ gg.game for gg in geekgames ])
        games.update(playedGames)
        for gg in geekgames:
            gg.game = games[gg.game]
        if options.excludeExpansions:
            geekgames = [ gg for gg in geekgames if not gg.game.expansion ]
        self.collections[key] = geekgames
        return geekgames

    def getCollections(self):
        import game_collections
        if self.colls is None:
            cs = game_collections.getAllCollectionsForGeek(self.context, True)
            self.colls = {}
            for c in cs:
                self.colls[c.index] = c
        return self.colls

    def getCollection(self, index):
        return self.getCollections()[index]

    def getAllCategories(self, options):
        items = self.getAllGeekGamesWithOptions(options)
        cats = []
        for gg in items:
            for c in gg.game.categories:
                if c not in cats:
                    cats.append(c)
        return cats

    def getAllMechanics(self, options):
        items = self.getAllGeekGamesWithOptions(options)
        cats = []
        for gg in items:
            for c in gg.game.mechanics:
                if c not in cats:
                    cats.append(c)
        return cats

    def getAllDesigners(self, options):
        items = self.getAllGeekGamesWithOptions(options)
        cats = []
        for gg in items:
            for c in gg.game.designers:
                if c not in cats:
                    cats.append(c)
        return cats

    def getAllGamesExcludingBooks(self, options):
        items = self.getAllGeekGamesWithOptions(options)
        items = [ gg for gg in items if not "Book" in gg.game.categories ]
        return items

    def getOwnedGamesExcludingBooks(self, options):
        items = self.getAllGeekGamesWithOptions(options)
        items = [ gg for gg in items if gg.owned ]
        items = [ gg for gg in items if not "Book" in gg.game.categories ]
        return items

    def getOwnedGames(self):
        import library
        opts = library.Thing()
        opts.excludeExpansions = False
        opts.excludeTrades = False
        items = self.getAllGeekGamesWithOptions(opts)
        items = [ gg for gg in items if gg.owned ]
        return items

    def getPreviouslyOwnedGamesExcludingBooks(self, options):
        items = self.getAllGamesExcludingBooks(options)
        items = [ gg for gg in items if gg.prevowned and not gg.owned ]
        return items

    def getPreviouslyOwnedGames(self, options):
        items = self.getAllGeekGamesWithOptions(options)
        if self.geek == "Friendless":
            with open("/tmp/before.txt", "w") as f:
                import pprint
                pprint.pprint(items, f)
        items = [ gg for gg in items if gg.prevowned ]
        if self.geek == "Friendless":
            with open("/tmp/after.txt", "w") as f:
                import pprint
                pprint.pprint(items, f)
        return items

    def getAllRatedGames(self, options):
        data = self.getAllGeekGamesWithOptions(options)
        return [ d for d in data if d.rating > 0 ]

    def getAllPlayedGames(self, options):
        data = self.getAllGeekGamesWithOptions(options)
        return [ d for d in data if d.plays > 0 ]

    def __getAllPlays(self):
        import dbaccess
        if self.allPlays is None:
            plays = dbaccess.getPlays(self.geek, None, None)
            self.allPlays = self.__reconstructPlays(plays)
        return self.allPlays

    def filterPlays(self, startDate, endDate):
        (result, messages) = self.__getAllPlays()
        if startDate is not None or endDate is not None:
            # dateless plays can never match any criteria with a date
            result = [ p for p in result if p.dt is not None ]
        return [ p for p in result if (startDate is None or p.dt >= startDate) and (endDate is None or p.dt <= endDate) ], messages

    def getPlaysForDescribedRange(self, fields):
        import library
        (year, month, day, args, startDate, endDate) = library.getDateRangeForDescribedRange(fields)
        (plays,  messages) = self.filterPlays(startDate, endDate)
        return plays, messages, year, month, day, args

    def addPlaysDataToGeekGames(self, geekgames):
        import library, datetime
        plays = self.getPlaysForDescribedRange([])[0]
        byGame = {}
        for p in plays:
            p.game.plays = []
            byGame[p.game.bggid] = p.game
            for e in p.expansions:
                e.plays = []
                byGame[e.bggid] = e
        for p in plays:
            p.game.plays.append(p)
            for e in p.expansions:
                e.plays.append(p)
        today = datetime.date.today()
        if today.month == 2 and today.day == 29:
            oneYearAgo = datetime.date(today.year-1, 2, 28)
        else:
            oneYearAgo = datetime.date(today.year-1, today.month, today.day)
        oneYearAgo = oneYearAgo.strftime("%Y-%m-%d")
        for gg in geekgames:
            g = byGame.get(gg.bggid)
            if g is None:
                (gg.plays, gg.firstPlay, gg.lastPlay, gg.monthsPlayed, gg.playsInLastYear) = (0, None, None, 0, 0)
            else:
                data = g.plays
                playCount = 0
                playsInLastYear = 0
                first = None
                last = None
                playsByMonth = library.Counts()
                for play in data:
                    if play.date > oneYearAgo:
                        playsInLastYear += play.count
                    playCount += play.count
                    if ((first is None) or (play.date < first)) and not play.date.endswith("00"):
                        first = play.date
                    if ((last is None) or (play.date > last)) and not play.date.endswith("00"):
                        last = play.date
                    playDateMonth = play.date[:7]
                    playsByMonth.add(playDateMonth, play.count)
                monthCount = len(playsByMonth)
                try:
                    firstPlay = library.parseYYYYMMDD(first)
                except ValueError:
                    firstPlay = None
                try:
                    lastPlay = library.parseYYYYMMDD(last)
                except ValueError:
                    lastPlay = None
                (gg.plays, gg.firstPlay, gg.lastPlay, gg.monthsPlayed, gg.pbm, gg.playsInLastYear) = (playCount, firstPlay, lastPlay, monthCount, playsByMonth, playsInLastYear)

    def __reconstructPlays(self, playsData):
        import plays
        ids = []
        for p in playsData:
            if p.game not in ids:
                ids.append(p.game)
        games = self.getGames(ids)
        moreGames = []
        for g in games.values():
            if g.expansion:
                for bg in g.basegames:
                    if bg not in ids and bg not in moreGames:
                        moreGames.append(bg)
        mgames = self.getGames(moreGames)
        for (id,  g) in mgames.items():
            games[id] = g
        result = []
        for p in playsData:
            game = games[p.game]
            result.append(plays.Play(game, [], p.playDate, p.quantity, p.raters, p.ratingsTotal, p.location))
        (result, messages) = _inferExtraPlays(games, result)
        processPlays(result)
        result.sort()
        return result,  messages

    def getAllSeries(self):
        import mydb, library
        if self.series is not None:
            return self.series
        sql = "select name, game from series"
        data = mydb.query(sql, [])
        self.series = library.DictOfSets()
        games = []
        for (name, bggid) in data:
            if bggid not in games:
                games.append(bggid)
        games = self.getGames(games)
        for (name, bggid) in data:
            g = games.get(bggid)
            if g is None:
                continue
            self.series.add(name, g)
        return self.series

def processPlays(plays):
    for p in plays:
        p.gameurl = p.game.url
        p.gamename = p.game.name
        p.expansionNames = ", ".join([e.name for e in p.expansions])

def getGames(ids):
    """ Returns map from long to Game objects from the database. """
    import library, dbaccess
    if len(ids) == 0:
        return {}
    ids = library.uniq(ids)
    games = dbaccess.getGames(ids)
    mechanics = library.DictOfSets()
    categories = library.DictOfSets()
    publishers = library.DictOfSets()
    designers = library.DictOfSets()
    if len(ids) > 0:
        ds = dbaccess.getGameDesigners(ids)
        dids = [ t.designerId for t in ds ]
        if len(dids) > 0:
            dess = dbaccess.getDesigners(dids)
            for t in ds:
                designers.add(t.gameId, dess[t.designerId])
        ps = dbaccess.getGamePublishers(ids)
        pids = [ t.publisherId for t in ps ]
        if len(pids) > 0:
            pubs = dbaccess.getPublishers(pids)
            for t in ps:
                publishers.add(t.gameId, pubs[t.publisherId])
        ms = dbaccess.getGameMechanics(ids)
        for m in ms:
            mechanics.add(m.gameId, m.mechanic)
    if len(ids) > 0:
        cs = dbaccess.getGameCategories(ids)
        for c in cs:
            categories.add(c.gameId, c.category)
    (basegames, expData) = getMetadata()
    for g in games.values():
        g.basegames = []
        g.expansions = []
    for (b, e) in expData:
        if games.get(b) is not None and e not in basegames:
            games[b].expansions.append(e)
        if games.get(e) is not None and e not in basegames:
            games[e].basegames.append(b)
            games[e].expansion = True
    for g in games.values():
        g.url = GAME_URL % g.bggid
        g.mechanics = mechanics[g.bggid]
        g.categories = categories[g.bggid]
        g.publishers = publishers[g.bggid]
        g.designers = designers[g.bggid]
    return games

METADATA = None

def getMetadata():
    global METADATA
    if METADATA is None:
        import mydb, library
        sql = "select ruletype, bggid from metadata"
        ruleData = mydb.query(sql, [])
        basegames = [ int(gameId) for (rule, gameId) in ruleData if rule == library.BASEGAME ]
        # games which are marked wrongly as basegames in BGG!
        expansions = [ int(gameId) for (rule, gameId) in ruleData if rule == library.EXPANSION ]
        sql = "select basegame, expansion from expansions"
        expData = mydb.query(sql, [])
        expData = [ (b,e) for (b,e) in expData if b not in expansions ]
        METADATA = basegames, expData
    return METADATA

def _inferExtraPlays(games, plays):
    import library
    result = []
    messages = []
    playsByDate = library.DictOfLists()
    playCountByMonth = library.Counts()
    for play in plays:
        playsByDate.add(play.date, play)
        playCountByMonth.add(play.date[:7])
    for date in playsByDate.keys():
        datePs = playsByDate[date]
        count = 0
        mms = []
        while True:
            mms = []
            (rs, ms, changed) = _inferExtraPlaysForADate(games, datePs)
            mms = mms + ms
            if not changed:
                break
            count += 1
            if count == 200:
                mms = mms + ["Got really confused"]
                break
            datePs = rs
        result = result + rs
        messages = messages + mms
    return (result, messages)

def __intersect(lista, listb):
    return len([a for a in lista if a in listb]) > 0

def _inferExtraPlaysForADate(games, plays):
    import library
    from plays import Play
    result = []
    messages = []
    for play in plays:
        if play.game.expansion:
            for bgplay in plays:
                if play is bgplay:
                    continue
                exids = [ x.bggid for x in bgplay.expansions ]
                if (bgplay.game.bggid in play.game.basegames or __intersect(play.game.basegames, exids)) and play.game not in bgplay.expansions:
                    nq = min(play.count, bgplay.count)
                    play.count = play.count - nq
                    bgplay.count = bgplay.count - nq
                    p = Play(bgplay.game, bgplay.expansions + [play.game] + play.expansions, bgplay.date, nq, bgplay.raters, bgplay.ratingsTotal,  "")
                    #messages.append(u"%s Added %d plays of %s to %s" % (p.date, nq, play.game.name, p.game.name))
                    newps = [p]
                    if play.count > 0:
                        newps.append(play)
                    if bgplay.count > 0:
                        newps.append(bgplay)
                    orig = len(plays)
                    others = [ op for op in plays if op is not play and op is not bgplay ]
                    messages.append(u"%s %s expands %s %d + %d <= %d" % (unicode(play.date), play.game.name.decode('utf-8'), bgplay.game.name.decode('utf-8'), len(newps), len(others), orig))
                    return others + newps, messages, True
            # no known basegame
            if len(play.game.basegames) == 1:
                basegame = play.game.basegames[0]
                if games.get(basegame) is None:
                    gs = getGames([basegame])
                    if gs.get(basegame) is None:
                        raise Exception("Never heard of game %s which is the base game of %s" % (str(basegame), play.game.name))
                    games[basegame] = gs[basegame]
                p = Play(games[basegame], [play.game] + play.expansions, play.date, play.count, play.raters, play.ratingsTotal,  "")
                others = [ op for op in plays if op is not play ]
                #messages.append(u"%s Inferred a play of %s from %s, %s\nothers = %s\nplays = %s" % (play.date, games[basegame].name, play.game.name, str(p.expansions), str(others), str(plays)))
                return others + [p], messages, True
            else:
                messages.append("Can't figure out what %s expanded on %s: %s" % (play.game.name, play.date, library.gameNames(play.game.basegames, games)))
            messages.append("No idea about %s" % bgplay.game.name)
        result.append(play)
    return result, messages, False

def createEmptyGeekGame(g):
    import library
    gg = library.Thing("GeekGame")
    gg.rating = 0
    gg.game = g
    gg.owned = False
    gg.want = 0
    gg.wish = 0
    gg.trade = 0
    gg.plays = 0
    gg.prevowned = 0
    gg.comment = ""
    gg.wanttobuy = 0
    gg.wanttoplay = 0
    gg.preordered = 0
    gg.bggid = g.bggid
    gg.utilisation = 0.0
    gg.timeweighted = 0.0
    return gg
