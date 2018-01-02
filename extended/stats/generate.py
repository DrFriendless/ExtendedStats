import math, time

GAME_XML_URL = "http://boardgamegeek.com/xmlapi/game/%d"
GAME_URL = "http://www.boardgamegeek.com/game/%d"
LAMBDA = math.log(0.1) / -10.0
START_YEAR = 2003
END_YEAR = time.localtime()[0]
END_MONTH = time.localtime()[1]
USED_YEARS = [ str(y) for y in range(START_YEAR, END_YEAR+1) ]
HUBER_BASELINE = 4.5

def addCollectionSummary(context, groups):
    import library
    opts = library.Thing()
    opts.excludeExpansions = False
    opts.excludeTrades = False
    allGeekGames = context.substrate.getAllGeekGamesWithOptions(opts)
    allGames = {}
    for gg in allGeekGames:
        allGames[gg.game.bggid] = gg
    for group in groups:
        geekGames = [ allGames.get(g.bggid) for g in group.games ]
        geekGames = [ gg for gg in geekGames if gg is not None ]
        rated = [ gg for gg in geekGames if gg.rating > 0 ]
        group.count = len(group.games)
        group.rated = len(rated)
        group.sumrating = sum([gg.rating for gg in rated])
        if group.rated > 0:
            group.rating = group.sumrating * 1.0 / group.rated
        else:
            group.rating = 0
        group.rating = int(group.rating * 100.0)/100.0
        plays = [gg.plays for gg in geekGames]
        plays.sort()
        group.plays = sum(plays)
        group.hindex = 0
        if len(geekGames) > 0:
            group.meanPlays = group.plays * 1.0 / len(geekGames)
            group.meanPlays = int(group.meanPlays * 100.0)/100.0
            group.medianPlays = plays[len(plays)/2]
            sumu = sum([gg.utilisation for gg in geekGames])
            group.utilisation = int(sumu / group.count * 100.0) / 100.0
            plays.sort()
            plays.reverse()
            while group.hindex < len(geekGames) and plays[group.hindex] > group.hindex:
                group.hindex += 1
        else:
            group.medianPlays = 0
            group.meanPlays = 0
            group.utilisation = 0

def getPlayLocationsData(context):
    import library, mydb
    sql = "select game, quantity, location, playDate from plays where geek = %s and location is not null and location != ''"
    data = mydb.query(sql,  [context.geek])
    games = context.substrate.getGames([d[0] for d in data])
    byLocation = {}
    countByLocation = library.Counts()
    for (gid,  quantity,  location, playDate) in data:
        countByLocation.add(location,  quantity)
        if byLocation.get(location) is None:
            byLocation[location] = {}
        byGame = byLocation[location]
        if byGame.get(gid) is None:
            byGame[gid] = library.Thing()
            byGame[gid].game = games[gid]
            byGame[gid].quantity = 0
            byGame[gid].dates = []
        record = byGame[gid]
        record.quantity = record.quantity + quantity
        if playDate not in record.dates:
            record.dates.append(playDate)
    result = []
    for loc in countByLocation.descending():
        item = library.Thing()
        item.location = loc
        item.count = countByLocation[loc]
        item.games = []
        for (game,  data) in byLocation[loc].items():
            gd = library.Thing()
            gd.first = False
            gd.game = data.game
            gd.count = data.quantity
            gd.dates = []
            names = []
            for d in data.dates:
                if d is None:
                    continue
                dt = library.Thing()
                dt.name = "%4d/%02d/%02d" % (d.year,  d.month,  d.day)
                dt.url = "/%d/%d" % (d.year,  d.month)
                if dt.name not in names:
                    gd.dates.append(dt)
                    names.append(dt.name)
            gd.dates.sort(lambda d1,  d2: -cmp(d1.name,  d2.name))
            item.games.append(gd)
        item.games.sort(lambda g1,  g2: cmp(g1.game.name,  g2.game.name))
        item.games[0].first = True
        item.games[0].rowspan = len(item.games)
        result.append(item)
    return result

def getPlayRatings(context):
    import library, mydb
    sql = "select sum(raters), sum(ratingsTotal), sum(quantity), game from plays where geek = %s group by game"
    data = mydb.query(sql, [context.geek])
    games = context.substrate.getGames([d[3] for d in data])
    plays = []
    for (raters, total, quantity, gid) in data:
        if games.get(gid) is None or raters == 0:
            continue
        g = games.get(gid)
        g.raters = raters
        g.total = total
        g.count = quantity
        g.average = int(float(total) / float(raters) * 100.0) / 100.0
        plays.append(g)
    plays.sort(library.gameName)
    return plays

def addGeekData(geek, plays):
    import mydb
    ids = []
    for p in plays:
        if p.game.bggid not in ids:
            ids.append(p.game.bggid)
    ggs = mydb.query("select game, rating from geekgames where geek = %s", [geek])
    ratings = {}
    for (gid, rating) in ggs:
        ratings[gid] = rating
    for p in plays:
        if ratings.get(p.game.bggid) is not None:
            p.rating = ratings[p.game.bggid]
        else:
            p.rating = -1

def calcFriendless(data):
    import library
    data.sort(lambda g1, g2: -cmp(g1, g2))
    ld = len(data)
    tens = 0
    zeros = 0
    for p in data:
        if p >= 10:
            tens += 1
        elif p == 0:
            zeros += 1
    if ld == 0:
        friendless = 0
    elif tens == ld:
        friendless = data[-1]
    else:
        friendless = data[-tens-1]
        if friendless == 0:
            friendless = tens - zeros
    if ld == 0:
        cfm = 0.0
        utilisation = 0.0
    else:
        tot = 0.0
        for p in data:
            tot = tot + library.cdf(p, LAMBDA)
        utilisation = int(tot / ld * 10000.0) / 100.0
        cfm = int(library.invcdf(tot / ld, LAMBDA) * 100.0) / 100.0
    return friendless, utilisation, cfm, tens, zeros

def calculateCollectionData(coll, title):
    import library
    result = library.Thing()
    result.title = title
    result.count = len(coll)
    result.bggAvg = int(library.average([gg.game.average for gg in coll]) * 100.0) / 100.0
    rated = [gg for gg in coll if gg.rating >= 0]
    result.yourAvg = int(library.average([gg.rating for gg in rated]) * 100.0) / 100.0
    totalPlays = sum(gg.plays for gg in coll)
    denom = len(coll)
    if denom == 0:
        denom = 1000000
    result.avgPlays = int(float(totalPlays) / denom * 100.0) / 100.0
    (result.friendless, result.utilisation, result.cfm, result.ten, result.zero) = calcFriendless([g.plays for g in coll])
    return result

def getConsistencyData(context, selector, monthsBack):
    import library, datetime
    today = datetime.date.today()
    todayMonth = today.month
    todayYear = today.year
    startDate = today - datetime.timedelta(monthsBack * 31)
    startMonth = startDate.month
    startYear = startDate.year
    months = []
    m = startMonth
    y = startYear
    while y * 12 + m <= todayYear * 12 + todayMonth:
        months.append((m, y))
        m += 1
        if m > 12:
            m = 1
            y += 1
    opts = library.Thing()
    opts.excludeExpansions = True
    opts.excludeTrades = False
    geekgames = selector.getGames(context, opts)
    geekgames.sort(lambda g1, g2: -cmp(g1.plays, g2.plays))
    geekgames = [ gg for gg in geekgames if gg.lastPlay is not None and gg.lastPlay >= startDate ]
    if len(geekgames) > 0 and geekgames[0].plays > 10:
        geekgames = [ gg for gg in geekgames if gg.plays >= 10 ]
    geekgames.sort(lambda g1, g2: -cmp(g1.monthsPlayed, g2.monthsPlayed))
    geekgames = geekgames[:100]
    data = []
    for gg in geekgames:
        t = library.Thing()
        t.name = gg.game.name
        t.firstPlay = ("%04d-%02d-%02d" % (gg.firstPlay.year, gg.firstPlay.month, gg.firstPlay.day))
        t.monthsPlayed = gg.monthsPlayed
        fp = datetime.date(gg.firstPlay.year, gg.firstPlay.month, 1)
        t.monthsSinceFirstPlay = int((today - fp).days * 12 / 365.25)
        t.propMonths = 100
        if t.monthsSinceFirstPlay > 0:
            t.propMonths = int(gg.monthsPlayed * 100.0 / t.monthsSinceFirstPlay)
        t.played = [ playedData(gg, m, y) for (m,y) in months ]
        t.plays = gg.plays
        t.rating = gg.rating
        data.append(t)
    return data

def playedData(gg, m, y):
    import library
    t = library.Thing()
    mstr = "%04d-%02d" % (y, m)
    t.n = gg.pbm[mstr]
    if t.n > 0:
        t.tooltip = "%s (%d)" % (mstr, t.n)
    else:
        t.tooltip = ""
    t.m = m
    t.y = y
    if t.n > 0:
        t.clss = getPlaysClass(t.n)
    else:
        t.clss = None
    return t

def getPlaysClass(n):
    if n == 0:
        #fill = WHITE
        return "plays0"
    elif n == 1:
        #fill = RED
        return "plays1"
    elif n < 3:
        #fill = ORANGE
        return "plays2"
    elif n < 5:
        #fill = YELLOW
        return "plays3"
    elif n < 10:
        #fill = YELLOWGREEN
        return "plays4"
    elif n < 25:
        #fill = GREEN
        return "plays5"
    else:
        #fill = DARKGREEN
        return "plays6"

def produceGiniDataFromPogoDate(data):
    if len(data) == 0:
        return 1.0, data
    totalPlays = sum([gg.plays for gg in data])
    expectedPerGame = totalPlays * 1.0 / len(data)
    betweenCurves = 0.0
    playsSum = 0
    expectedSum = 0.0
    denom = 0.0
    for gg in data:
        playsSum += gg.plays
        expectedSum += expectedPerGame
        betweenCurves += expectedSum - playsSum
        denom += expectedSum
        gg.totalPlays = totalPlays
    if denom == 0.0:
        return None, None
    giniCoefficient = betweenCurves / denom
    return giniCoefficient, data

def getPogoData(context, selector):
    import library
    opts = context.options.pogo
    geekgames = selector.getGames(context, opts)
    title = "For Games You Own"
    if opts.excludeTrades:
        title += " Excluding Games You Are Trying to Trade"
    if opts.excludeExpansions:
        title += " Excluding Expansions"
    collections = [calculateCollectionData(geekgames, title)]
    result = []
    for gg in geekgames:
        r = library.Thing()
        if gg.game is not None:
            r.name = gg.game.name
            r.rank = gg.game.rank
            r.average = gg.game.average
            r.url = gg.game.url
            r.usersrated = gg.game.usersrated
            r.expansion = gg.game.expansion
            r.plays = gg.plays
            r.utilisation = gg.utilisation
            r.rating = gg.rating
            result.append(r)
    result.sort(lambda gg1, gg2: -cmp(gg1.plays, gg2.plays))
    return result, collections

def getChecklistData(context):
    import library
    geekgames = context.substrate.getOwnedGames()
    result = []
    for gg in geekgames:
        t = library.Thing()
        if gg.game:
            t.name = gg.game.name
        else:
            t.name = "Unknown %d" % gg.bggid
        result.append(t)
    result.sort(lambda t1, t2: cmp(t1.name.lower(), t2.name.lower()))
    return result

def collatePlays(playsData):
    import library, plays, substrate
    exps = library.DictOfSets()
    counts = library.Counts()
    ts = None
    for play in playsData:
        exps.addAll(play.game, play.expansions)
        counts.add(play.game, play.count)
        ts = play.date
    result = []
    for g in counts.keys():
        play = plays.Play(g, exps[g], ts, counts[g], 0, 0,  "")
        result.append(play)
    substrate.processPlays(result)
    result.sort()
    return result

def florenceData(playsData):
    import library
    count = library.Counts()
    for pg in playsData:
        count.add(pg.game.subdomain, pg.count)
    return count

def morePieChartData(playsData):
    import library
    count = library.Counts()
    for pg in playsData:
        count.add(pg.game.name, pg.count)
    return count

def getLagData(context):
    import library
    options = library.Thing()
    options.excludeTrades = False
    options.excludeExpansions = True
    geekgames = context.substrate.getAllGamesExcludingBooks(options)
    geekgames = [ gg for gg in geekgames if gg.plays > 0 and gg.firstPlay is not None ]
    result = library.Counts()
    for gg in geekgames:
        playYear = gg.firstPlay.year
        releaseYear = gg.game.yearpublished
        diff = playYear - releaseYear
        if diff < 0:
            diff = 0
        result.add(diff)
    return result

def getNewPlaysData(context):
    import library
    options = library.Thing()
    options.excludeTrades = False
    options.excludeExpansions = True
    geekgames = context.substrate.getAllGamesExcludingBooks(options)
    geekgames = [ gg for gg in geekgames if gg.plays > 0 and gg.firstPlay is not None ]
    return [ gg.firstPlay for gg in geekgames ]

def getLifetimeData(context):
    import library, datetime
    options = library.Thing()
    options.excludeTrades = False
    options.excludeExpansions = False
    geekgames = context.substrate.getAllGamesExcludingBooks(options)
    geekgames = [ gg for gg in geekgames if gg.plays > 0 and gg.firstPlay is not None and gg.lastPlay != gg.firstPlay ]
    result = []
    for gg in geekgames:
        lifetime = (gg.lastPlay - gg.firstPlay).days+1
        try:
            published = datetime.date(gg.game.yearpublished, 1, 1)
        except ValueError:
            published = datetime.date(1900, 1, 1)
        age = (datetime.date.today() - published).days + 1
        result.append((lifetime, gg.game.expansion, gg.owned, age))
    return result

def getLifetimeByRatingData(context):
    import library
    options = library.Thing()
    options.excludeTrades = False
    options.excludeExpansions = False
    geekgames = context.substrate.getAllGamesExcludingBooks(options)
    geekgames = [ gg for gg in geekgames if gg.plays > 0 and gg.firstPlay is not None and gg.lastPlay != gg.firstPlay and gg.rating >= 0]
    return [ ((gg.lastPlay - gg.firstPlay).days+1, gg.rating) for gg in geekgames ]

def getPlaysTableData(context):
    import library
    options = library.Thing()
    options.excludeTrades = False
    options.excludeExpansions = True
    geekgames = context.substrate.getAllGamesExcludingBooks(options)
    geekgames = [ gg for gg in geekgames if gg.plays > 0 and gg.firstPlay is not None ]
    result = []
    for gg in geekgames:
        result.append(gg.firstPlay)
    return result

def __addAllPlaysByGame(dest, src):
    for (game, count) in src.items():
        if dest.get(game) is None:
            dest[game] = count
        else:
            dest[game] = dest[game] + count

def getPBMData(context):
    if context.pbm is not None:
        return context.pbm
    import period
    opts = context.options.pbm
    playData = context.substrate.getPlaysForDescribedRange([])[0]
    owned = context.substrate.getOwnedGames()
    ratingsForGames = {}
    for gg in owned:
        ratingsForGames[gg.game] = gg.rating
    if opts.excludeTrades:
        owned = [ gg for gg in owned if not gg.trade ]
    if opts.excludeExpansions:
        owned = [ gg for gg in owned if not gg.game.expansion ]
    months = {}
    years = {}
    games = []
    for play in playData:
        if not play.year:
            mn = "0000-00"
            play.year = 0
            play.month = 0
            play.day = 0
        else:
            mn = "%4d-%02d" % (play.year, play.month)
        if months.get(mn) is None:
            months[mn] = period.Month(mn, opts)
        m = months[mn]
        d = "%4d-%02d-%02d" % (play.year, play.month, play.day)
        m.daysPlayedOn.add(d)
        m.count = m.count + play.count
        m.plays.append(play)
        m.played.add(play.game)
        if play.game not in games:
            games.append(play.game)
        for g in play.expansions:
            m.expPlayed.add(g)
            if g not in games:
                games.append(g)
    #
    months = months.values()[:]
    months.sort()
    if len(months) > 0 and months[0].name == "0000-00":
        months = months[1:] + [months[0]]
    # calculate year-to-date stuff
    playedSoFar = set()
    expPlayedSoFar = set()
    totalPlays = 0
    ever = period.Period("Ever", opts)
    for m in months:
        y = years.get(m.year)
        if y is None:
            y = period.YearToDate(m.year, opts)
            years[m.year] = y
        playTime = 0
        for play in m.plays:
            m.addPlaysForGame(play.game, play.count)
            fd = y.addPlaysForGame(play.game, play.count)
            if 5 in fd:
                m.nickels.add(play.game)
            if 10 in fd:
                m.dimes.add(play.game)
            fd = ever.addPlaysForGame(play.game, play.count)
            if 5 in fd:
                m.everNickels.add(play.game)
            if 10 in fd:
                m.everDimes.add(play.game)
            if 25 in fd:
                m.everQuarters.add(play.game)
            if 100 in fd:
                m.everDollars.add(play.game)
            for e in play.expansions:
                m.addPlaysForGame(e, play.count)
                y.addPlaysForGame(e, play.count)
                ever.addPlaysForGame(e, play.count)
            playTime = playTime + play.count * play.game.playtime
        m.playHours = int((playTime + 30) / 60)
        y.count += m.count
        totalPlays += m.count
        y.played |= m.played
        m.new |= m.played
        m.new -= playedSoFar
        m.newExpPlayed |= m.expPlayed
        m.newExpPlayed -= expPlayedSoFar
        playedSoFar |= m.played
        expPlayedSoFar |= m.expPlayed
        y.new |= m.new
        y.newExpPlayed |= m.newExpPlayed
        m.countYtd = y.count
        m.distinctYtd = len(y.played)
        m.newYtd = len(y.new)
        m.distinctEver = len(playedSoFar)
        m.playsEver = totalPlays
        m.percentPlayed = ever.calculatePercentPlayed(owned)
        m.percentPlayedYTD = y.calculatePercentPlayed(owned)
        m.hindexToDate = y.calcHIndex()
        m.hindexEver = ever.calcHIndex()
    # patch in other values we want to display
    playsByGame = {}
    for m in months:
        m.calculateProperties(playsByGame, ratingsForGames)
        __addAllPlaysByGame(playsByGame, m.playsByGame)
    months.reverse()
    if len(months) > 0 and months[0].name == "0000-00":
        months = months[1:]
    context.pbm = months
    return months

def sgoyt(param):
    import sitedata, views, xml.dom.minidom, library, selectors, os
    param = int(param)
    dest = os.path.join(sitedata.dbdir, "geeklist_%d.xml" % (param,))
    url = selectors.GEEKLIST_URL % param
    success = library.getFile(url, dest)
    if not success:
        raise views.BadUrlException("Failed to download geeklist XML from %s" % url)
    data = []
    try:
        dom = xml.dom.minidom.parse(dest)
        geeklist = dom.getElementsByTagName("geeklist")[0]
        gameNodes = geeklist.getElementsByTagName("item")
        for gameNode in gameNodes:
            try:
                t = library.Thing()
                t.gid = int(gameNode.getAttribute("objectid"))
                t.user = gameNode.getAttribute("username")
                t.gamename = gameNode.getAttribute("objectname")
                data.append(t)
            except AttributeError:
                continue
        return data
    except xml.parsers.expat.ExpatError, e:
        raise views.BadUrlException("Error retrieving parsing geeklist: %s" % url)

def getPlayLoggingData(context):
    import library, mydb
    sql = "select location, count(location) c from plays where geek = %s and location is not null and location != '' group by location order by c desc limit 30"
    data = mydb.query(sql,  [context.geek])
    locations = [ l[0] for l in data ]
    sql = "select name, username, colour, sum(count) c from opponents where geek = %s group by name, username, colour order by c desc limit 30"
    data = mydb.query(sql,  [context.geek])
    players = []
    for (username, name, colour, junk) in data:
        t = library.Thing()
        if username is None:
            username = ''
        if name is None:
            name = ''
        if colour is None:
            colour = ''
        t.username = username
        t.name = name
        t.colour = colour
        players.append(t)
    return players, locations

def getMultiYearData(context):
    import library, mydb
    sql = "select year(playDate), game, sum(quantity) from plays where geek = %s group by year(playDate), game"
    data = mydb.query(sql, [context.geek])
    yearCounts = library.Counts()
    usedYears = [ int(y) for y in USED_YEARS ]
    for (y, gid, count) in data:
        if y in usedYears:
            yearCounts.add(gid, 1)
    gameIds = [x[0] for x in yearCounts.data.items() if x[1] > 1]
    games = context.substrate.getGames(gameIds)
    playsData = {}
    for gid in gameIds:
        playsData[gid] = {}
        for y in usedYears:
            playsData[gid][y] = whiteThing(0)
    for (y, gid, count) in data:
        if gid not in gameIds:
            continue
        try:
            t = playsData[gid][y]
        except KeyError:
            continue
        t.value = count
        t.colour = library.playsToColour(count)
    result = []
    for gid in gameIds:
        plays = [ playsData[gid][y] for y in usedYears ]
        total = sum([p.value for p in plays])
        result.append([ whiteThing(games[gid].name) ] + plays + [ whiteThing(total), whiteThing(yearCounts[gid]) ])
    result.sort(lambda r1, r2: cmp(r1[0].value.lower(), r2[0].value.lower()))
    return result, USED_YEARS + ["Total", "Count"]

def whiteThing(value):
    import library
    t = library.Thing()
    t.value = value
    t.colour = library.WHITE
    return t

def getPlayRateData(context, selector):
    if type(selector) == type("") or type(selector) == type(u""):
        import selectors
        selector = selectors.getSelectorFromString(selector)
    import library, math
    opts = library.Thing()
    opts.excludeExpansions = False
    opts.excludeTrades = False
    games = selector.getGames(context, opts)
    geekgames = context.substrate.getTheseGeekGames(games)
    if context.options.playrate.excludeUnrated:
        geekgames = [ gg for gg in geekgames if gg.rating > 0 ]
    names = library.DictOfDictOfLists()
    counts = library.DictOfCounts()
    for gg in geekgames:
        r = int(math.floor(gg.rating + 0.5))
        if r < 1:
            r = 0
        p = gg.plays
        if p > 25:
            p = 25
        names.add(p, r, gg.game.name)
        counts.add(p, r)
    return counts, names

def getRatingByPublishedYearData(context):
    import library
    opts = library.Thing()
    opts.excludeTrades = False
    opts.excludeExpansions = False
    data = context.substrate.getAllRatedGames(opts)
    # (rating, year) -> # of games
    counter = library.DictOfCounts()
    for gg in data:
        counter.add(gg.rating, gg.game.yearpublished)
    result = []
    for rating in counter.keys():
        for (year, count) in counter.get(rating).items():
            result.append((count, rating, year))
    return result

def getPlaysByPublishedYearData(context):
    import library
    data = context.substrate.getOwnedGamesExcludingBooks(context.options.obpy)
    result = library.DictOfLists()
    for gg in data:
        d = library.Thing()
        d.name = "%s (%d)" % (gg.game.name, gg.plays)
        d.plays = gg.plays
        d.bggid = gg.game.bggid
        result.add(gg.game.yearpublished, d)
    return result

def getOwnedByPublishedYearData(context):
    import library
    data = context.substrate.getOwnedGamesExcludingBooks(context.options.obpy)
    # (rating, year) -> # of games
    counter = library.DictOfCounts()
    for gg in data:
        counter.add(gg.rating, gg.game.yearpublished)
    result = []
    for rating in counter.keys():
        for (year, count) in counter.get(rating).items():
            result.append((count, rating, year))
    return result

def getMostPlayedUnplayedGames(context):
    import mydb
    sql = "select sum(quantity), game from plays group by game order by 1 desc"
    data = mydb.query(sql, [])
    sql = "select distinct game from plays where geek = %s"
    geekData = mydb.query(sql, [context.geek])
    played = [ x[0] for x in geekData ]
    ids = []
    remember = {}
    for (q, g) in data:
        if g not in played:
            ids.append(g)
            remember[g] = q
            if len(ids) == 20:
                break
    games = context.substrate.getGames(ids)
    for g in games.values():
        g.totalPlays = remember[g.bggid]
    games = games.values()[:]
    games.sort(lambda a,b: -cmp(a.totalPlays, b.totalPlays))
    return games

def addRanks(rows, valCol, rankCol, title):
    import math
    numRows = len(rows)
    data = rows[:]
    try:
        data.sort(lambda r1, r2: -cmp(r1.__dict__[valCol], r2.__dict__[valCol]))
    except KeyError:
        with open("/tmp/data.txt", "w") as f:
            f.write(" ".join([str(d.__dict__) for d in data if d.__dict__.get("owned") is None]))
    lastValue = -1000
    lastRank = 0
    for i, d in enumerate(data):
        if d.__dict__[valCol] == lastValue:
            percent = math.ceil(lastRank * 100.0 / numRows)
            d.__dict__[rankCol] = "%d (top %d%% of %s)" % (lastRank, percent, title)
        else:
            lastRank = i + 1
            percent = math.ceil(lastRank * 100.0 / numRows)
            d.__dict__[rankCol] = "%d (top %d%% of %s)" % (lastRank, percent, title)
            lastValue = d.__dict__[valCol]

def getAllCatsAndMecs():
    import mydb
    sql = "select distinct category from gameCategories order by 1"
    cats = mydb.query(sql)
    cats = [ c[0] for c in cats ]
    sql = "select distinct mechanic from gameMechanics order by 1"
    mecs = mydb.query(sql)
    mecs = [ c[0] for c in mecs ]
    return cats, mecs

def getNormRankedData(category):
    import substrate, mydb
    (cats, mecs) = getAllCatsAndMecs()
    minus = 0
    if not category:
        category = "all"
    parts = category.split("/", 1)
    for (index, part) in enumerate(parts):
        if part.startswith("-"):
            minus = int(part[1:])
            del part
            break
    if parts[0] == "all":
        title = "All Games"
        categoryClause = "(bggid not in (select gameId from gameCategories where category = 'Expansion for Base-game' or category = 'Book'))"
        params = []
    elif parts[0] == "category":
        if len(parts) == 1:
            raise Exception("No category specified")
        if parts[1] not in cats:
            raise Exception("Invalid category")
        title = "Category %s" % parts[1]
        categoryClause = "(bggid in (select gameId from gameCategories where category = %s))"
        params = [ parts[1] ]
    elif parts[0] == "mechanic":
        if len(parts) == 1:
            raise Exception("No mechanic specified")
        if parts[1] not in mecs:
            raise Exception("Invalid mechanic")
        title = "Mechanic %s" % parts[1]
        categoryClause = "(bggid in (select gameId from gameMechanics where mechanic = %s))"
        params = [ parts[1] ]
    else:
        raise Exception("No ranking criteria")
    sql = "select distinct bggid from geekgames, games where geekgames.game = games.bggid and rating > 0 and %s" % categoryClause
    data = mydb.query(sql, params)
    ids = [ d[0] for d in data ]
    games = substrate.getGames(ids)
    result = []
    ndata = getNormalisedRankingsDataForGames(ids)
    for (id, ng) in ndata.items():
        g = games.get(id)
        if g is None:
            continue
        g.normrank = ng.normrank
        result.append(g)
        result.sort(lambda g1, g2: cmp(g1.normrank, g2.normrank))
    return (cats, mecs, title, result[:1000])

def getTopRankedData(category):
    import substrate, mydb
    (cats, mecs) = getAllCatsAndMecs()
    minus = 0
    if not category:
        category = "all"
    parts = category.split("/", 1)
    for i in range(len(parts)):
        if parts[i].startswith("-"):
            minus = int(parts[i][1:])
            del parts[i]
            break
    if parts[0] == "all":
        title = "All Games"
        categoryClause = "(bggid not in (select gameId from gameCategories where category = 'Expansion for Base-game' or category = 'Book'))"
        params = []
    elif parts[0] == "category":
        if len(parts) == 1:
            raise Exception("No category specified")
        if parts[1] not in cats:
            raise Exception("Invalid category")
        title = "Category %s" % parts[1]
        categoryClause = "(bggid in (select gameId from gameCategories where category = %s))"
        params = [ parts[1] ]
    elif parts[0] == "mechanic":
        if len(parts) == 1:
            raise Exception("No mechanic specified")
        if parts[1] not in mecs:
            raise Exception("Invalid mechanic")
        title = "Mechanic %s" % parts[1]
        categoryClause = "(bggid in (select gameId from gameMechanics where mechanic = %s))"
        params = [ parts[1] ]
    else:
        raise Exception("No ranking criteria")
    sql = "select sum(rating), count(rating), name, bggid from geekgames, games where geekgames.game = games.bggid and rating > 0  and %s group by bggid order by 1 desc limit 1000" % categoryClause
    data = mydb.query(sql, params)
    ids = [ d[3] for d in data ]
    games = substrate.getGames(ids)
    result = []
    for (score, count, name, id) in data:
        g = games[id]
        result.append(g)
        g.score = int(score) - count * minus
        g.count = count
        g.totalPlays = 0
    rank = 1
    result.sort(lambda g1, g2: -cmp(g1.score, g2.score))
    for g in result:
        g.extrank = rank
        rank += 1
    if parts[0] == "all":
        ndata = getNormalisedRankingsData()
        for (id, ng) in ndata.items():
            g = games.get(id)
            if g is None:
                continue
            g.normrank = ng.normrank
    sql = "select sum(quantity), game from plays group by game"
    data = mydb.query(sql, [])
    for (q, g) in data:
        if games.get(g) is not None:
            games[g].totalPlays = q
    return (cats, mecs, title, result)

def getRawFrontPageData():
    import library, mydb
    sql = "select geek, totalPlays, distinctGames, top50, sdj, hindex, owned, want, wish, trade, prevOwned, friendless, cfm, utilisation, tens, zeros, ext100, mv from frontpagegeek"
    data = mydb.query(sql)
    rows = []
    for (geek, totalPlays, distinctGames, top50, sdj, hindex, owned, want, wish, trade, prevOwned, friendless, cfm, utilisation, tens, zeros, ext100, mv) in data:
        t = library.Thing()
        t.geek = geek
        t.totalPlays = totalPlays
        t.distinctGames = distinctGames
        t.top50 = top50
        t.sdj = sdj
        t.hindex = hindex
        t.owned = owned
        t.want = want
        t.wish = wish
        t.trade = trade
        t.prevOwned = prevOwned
        t.friendless = friendless
        t.cfm = cfm
        t.utilisation = utilisation
        t.tens = tens
        t.zeros = zeros
        t.ext100 = ext100
        t.mv = mv
        rows.append(t)
    return rows

def addPissingWarRanks(rows):
    addRanks(rows, "owned", "ownedRank", "Games Owned")
    addRanks(rows, "totalPlays", "playsRank", "Plays Recorded")
    addRanks(rows, "distinctGames", "distinctRank", "Distinct Games Played")
    addRanks(rows, "want", "wantRank", "Games on Want List")
    addRanks(rows, "wish", "wishRank", "Games on Wish List")
    addRanks(rows, "hindex", "hindexRank", "H-Index")
    addRanks(rows, "trade", "tradeRank", "Games For Trade")
    addRanks(rows, "sdj", "sdjRank", "Spiel des Jahre Winners Played")
    addRanks(rows, "top50", "top50Rank", "Top 50 Games Played")
    addRanks(rows, "ext100", "ext100Rank", "Extended Stats Top 100 Games Played")
    addRanks(rows, "mv", "mvRank", "Most Voted For Games Played")
    addRanks(rows, "prevOwned", "prevOwnedRank", "Games Previously Owned")
    addRanks(rows, "friendless", "friendlessRank", "Friendless Metric")
    addRanks(rows, "cfm", "cfmRank", "Continuous Friendless Metric")
    addRanks(rows, "zeros", "zerosRank", "Games Owned Played Zero Times")
    addRanks(rows, "tens", "tensRank", "Games Owned Played 10 Times")

def getAustraliaFrontPagePlaysData():
    import mydb
    all = getRawFrontPageData()
    sql = "select geek from users where country = %s"
    data = mydb.query(sql, ["Australia"])
    geeks = [ d[0] for d in data ]
    rows = [ a for a in all if a.geek in geeks ]
    addPissingWarRanks(rows)
    rows.sort(lambda g1, g2: cmp(g1.geek.lower(), g2.geek.lower()))
    return rows

def getFrontPagePlaysData():
    rows = getRawFrontPageData()
    addPissingWarRanks(rows)
    rows.sort(lambda g1, g2: cmp(g1.geek.lower(), g2.geek.lower()))
    return rows

class MPTData(object):
    def __init__(self, gg):
        self.gg = gg
        self.name = gg.game.name
        self.playsByMonth = {}

    def toMap(self):
        return {"name" : self.name, "playsByMonth":self.playsByMonth}

def getMostPlayedTimelineData(context):
    import library, datetime
    options = library.Thing()
    options.excludeTrades = False
    options.excludeExpansions = True
    ggs = context.substrate.getAllPlayedGames(options)
    ggs = [ gg for gg in ggs if "plays"in gg.game.__dict__ ]
    ggs.sort(lambda g1, g2: -cmp(g1.plays, g2.plays))
    if len(ggs) > 20:
        ggs = ggs[:20]
    minDate = None
    mostPlays = 0
    for gg in ggs:
        if gg.firstPlay is not None and (minDate is None or gg.firstPlay < minDate):
            minDate = gg.firstPlay
    if minDate is None:
        return None, None, None
    today = datetime.date.today()
    if library.daysSince(minDate) > 12 * 366:
        minDate = today - datetime.timedelta(days=12 * 366)
    result = [ MPTData(gg) for gg in ggs ]
    ty = today.year
    tm = today.month
    for mptd in result:
        accum = 0
        y = minDate.year
        m = minDate.month
        while y < ty or (y == ty and m <= tm):
            mptd.playsByMonth["%04d-%02d" % (y,m)] = 0
            m += 1
            if m > 12:
                m = 1
                y += 1
        for p in mptd.gg.game.plays:
            if p.date.endswith("00"):
                accum += p.count
                continue
            d = datetime.datetime.strptime(p.date, "%Y-%m-%d").date()
            if d < minDate:
                d = minDate
            key = "%04d-%02d" % (d.year, d.month)
            mptd.playsByMonth[key] += p.count
            accum += p.count
            if accum > mostPlays:
                mostPlays = accum
    for i in range(len(result)):
        result[i].colour = library.COLOURS[i]
    return minDate, result, mostPlays

def getFirstPlayVsRatingData(geek):
    import mydb
    sql = "select game, min(playDate), rating from geekgames inner join plays using (geek, game) where geek = %s and rating > 0 group by game order by 2 asc"
    data = mydb.query(sql, [geek])
    return data

def getGeekYears(geek):
    import mydb
    sql = "select y from (select y, count(distinct m) cm from (select year(playDate) y, month(playDate) m from plays where geek = %s) ym group by y) yc where cm > 3"
    data = mydb.query(sql, [geek])
    return [ int(d[0]) for d in data ]

def getShouldPlayGames(context, owned):
    import library,  datetime
    substrate = context.substrate
    options = library.Thing()
    options.excludeTrades = False
    options.excludeExpansions = True
    if owned:
        data = substrate.getOwnedGamesExcludingBooks(options)
    else:
        data = substrate.getAllGamesExcludingBooks(options)
    sql = "select games.bggid, rating from geekgames, games where geekgames.game = games.bggid and geekgames.geek = %s"
    if owned:
        sql += " and owned"
    data = [ d for d in data if d.lastPlay is not None ]
    now = datetime.date.today()
    result = []
    for g in data:
        gg = library.Thing()
        gg.lastPlay = g.lastPlay
        gg.rating = g.rating
        gg.gameurl = g.game.url
        gg.gamename = g.game.name
        gg.sincePlayed = 0
        result.append(gg)
        if gg.lastPlay is None or gg.rating < 7:
            gg.score = 0.0
        else:
            r = gg.rating
            gg.lastPlayed = gg.lastPlay
            gg.sincePlayed = int((now - gg.lastPlay).days)
            gg.score = float(gg.sincePlayed * r * r * r * r)
    result.sort(lambda g1,  g2: -cmp(g1.score,  g2.score))
    return result

def getShouldPlayData(context):
    ggs = getShouldPlayGames(context,  False)
    return ggs[:20]

def getShouldPlayOwnData(context):
    ggs = getShouldPlayGames(context,  True)
    return ggs[:20]

def getFavouriteGamesByPublishedYear(context):
    import library
    opts = library.Thing()
    opts.excludeTrades = False
    opts.excludeExpansions = False
    geekgames = context.substrate.getAllRatedGames(opts)
    geekgames = [ gg for gg in geekgames if gg.rating >= 8 ]
    sorter = library.DictOfLists()
    for gg in geekgames:
        sorter.add(gg.game.yearpublished, gg.game)
    keys = sorter.keys()[:]
    keys.sort()
    result = []
    for k in keys:
        t = library.Thing()
        t.year = k
        t.games = sorter[k]
        t.count = len(t.games)
        t.games.sort(library.gameName)
        result.append(t)
    return result

def getWhatIfData(context):
    import library
    opts = context.options.pogo
    geekgames = context.substrate.getOwnedGamesExcludingBooks(opts)
    result = []
    for gg in geekgames:
        r = library.Thing()
        r.name = gg.game.name
        r.plays = gg.plays
        if gg.owned:
            r.own = "Yes"
        else:
            r.own = "No"
        result.append(r)
    result.sort(library.gameName)
    return result

def getPlaysCSVData(context):
    return context.substrate.getPlaysForDescribedRange([])[0]

def getFavourites(context, selector):
    result = getGeekGames(context, selector)
    result.sort(lambda t1, t2: -cmp(t1.fave, t2.fave))
    return result

def getGeekGames(context, selector):
    import math, library, datetime
    geekgames = selector.getGames(context, context.options.fave)
    result = []
    now = datetime.date.today()
    for gg in geekgames:
        t = library.Thing()
        t.rating = float(gg.rating)
        if t.rating <= 0:
            t.rating = 0
        t.owned = gg.owned
        t.trade = gg.trade
        t.want = gg.want
        t.wish = gg.wish
        t.prevowned = gg.prevowned
        t.wanttobuy = gg.wanttobuy
        t.wanttoplay = gg.wanttoplay
        t.preordered = gg.preordered
        t.gamename = gg.game.name
        t.gameurl = gg.game.url
        t.plays = int(gg.plays)
        t.hours = float(t.plays * gg.game.playtime / 60)
        t.firstPlay = gg.firstPlay
        t.lastPlay = gg.lastPlay
        t.monthsPlayed = int(gg.monthsPlayed)
        t.playsInLastYear = gg.playsInLastYear
        if t.lastPlay is not None and t.firstPlay is not None and t.monthsPlayed > 0 and t.rating > 0:
            t.flash = library.daysBetween(t.firstPlay,  t.lastPlay)
            t.lag = library.daysBetween(t.lastPlay,  datetime.date.today())
            t.flmr = t.flash * 1.0 / t.lag * t.monthsPlayed * t.rating
            if t.flmr <= 1:
                t.log = 0
            else:
                t.log = math.log(t.flmr)
            t.randyCox = int(t.log * 100)/100.0
        t.fave = int(t.rating * 5 + t.plays + t.monthsPlayed * 4 + t.hours)
        t.huber = int((t.rating - HUBER_BASELINE) * t.hours)
        if t.plays == 0:
            t.huberHeat = 0
        else:
            s = 1.0 + float(t.playsInLastYear) / t.plays
            hours = float(t.playsInLastYear * gg.game.playtime / 60.0)
            h = (t.rating - HUBER_BASELINE) * hours
            t.huberHeat = s * s * math.sqrt(float(t.playsInLastYear)) * h
            t.huberHeat = int(10 * t.huberHeat) / 10.0
        t.hours = int(math.floor(t.hours + 0.5))
        t.bggrank = gg.game.rank
        t.bggavg = int(gg.game.average * 10.0) / 10.0
        t.year = gg.game.yearpublished
        t.bggid = gg.game.bggid
        t.minPlayers = gg.game.minplayers
        t.maxPlayers = gg.game.maxplayers
        t.playTime = gg.game.playtime
        t.usersRated = gg.game.usersrated
        t.usersOwned = gg.game.usersowned
        t.subdomain = gg.game.subdomain
        t.weight = gg.game.averageweight
        if t.lastPlay is not None:
            t.sincePlayed = int((now - t.lastPlay).days)
        else:
            t.sincePlayed = 0
        if t.lastPlay is None or t.rating < 7:
            t.shouldPlayScore = 0.0
        else:
            r = t.rating
            t.shouldPlayScore = float(t.sincePlayed * r * r * r * r)
        t.utilisation = int(library.cdf(t.plays, LAMBDA) * 10000.0) / 100.0
        if t.rating > 0:
            t.whyOwn = float(t.sincePlayed) / t.rating / t.rating
        else:
            t.whyOwn = 0.0
        result.append(t)
    result.sort(lambda t1, t2: -cmp(t1.fave, t2.fave))
    return result

def calcHIndex(data):
    data = data[:]
    data.sort(lambda t1, t2: -cmp(t1.plays, t2.plays))
    hindex = 0
    while hindex < len(data) and data[hindex].plays > hindex:
        hindex += 1
    return hindex

def calcCorrelation(faves):
    # This uses the data generated by getFavourites.
    import math, library
    fs = [ x for x in faves if x.rating > 0 ]
    xs = [ x.rating for x in fs ]
    ys = [ x.bggavg for x in fs ]
    if len(xs) == 0:
        return 0.0
    x2s = [ x*x for x in xs ]
    y2s = [ y*y for y in ys ]
    xys = [ xs[i]*ys[i] for i in range(len(xs)) ]
    meanxy = library.mean(xys)
    meanx = library.mean(xs)
    meany = library.mean(ys)
    meanx2s = library.mean(x2s)
    meany2s = library.mean(y2s)
    d1 = math.sqrt(meanx2s - meanx * meanx)
    d2 = math.sqrt(meany2s - meany * meany)
    if d1 * d2 == 0.0:
        return 0.0
    c = (meanxy - meanx * meany) / (d1 * d2)
    return c

def calcCorrelationRankedOnly(faves):
    # This uses the data generated by getFavourites.
    import math, library
    fs = [ x for x in faves if x.rating > 0 and x.bggrank > 0 ]
    xs = [ x.rating for x in fs ]
    ys = [ x.bggavg for x in fs ]
    if len(xs) == 0:
        return 0.0
    x2s = [ x*x for x in xs ]
    y2s = [ y*y for y in ys ]
    xys = [ xs[i]*ys[i] for i in range(len(xs)) ]
    meanxy = library.mean(xys)
    meanx = library.mean(xs)
    meany = library.mean(ys)
    meanx2s = library.mean(x2s)
    meany2s = library.mean(y2s)
    d1 = math.sqrt(meanx2s - meanx * meanx)
    d2 = math.sqrt(meany2s - meany * meany)
    try:
        c = (meanxy - meanx * meany) / (d1 * d2)
    except ZeroDivisionError:
        c = 0
    return c

def getPlaysByQuarterData(context, startYear):
    import library, mydb
    sql = "select year(plays.playDate), quarter(plays.playDate), sum(plays.quantity), games.yearPublished from plays, games where plays.geek = %s and plays.game = games.bggid group by yearPublished, year(plays.playDate), quarter(plays.playDate)"
    data = mydb.query(sql, [context.geek])
    counts = library.DictOfCounts()
    for (year, quarter, quantity, pubYear) in data:
        if year < 2005:
            continue
        if pubYear < startYear:
            pubYear = startYear
        quarterKey = "%d-%d" % (year, quarter)
        counts.add(quarterKey, pubYear, int(quantity))
    return counts

def hasPlaysData(context):
    import mydb
    sql = "select sum(plays.quantity) from plays where plays.geek = %s"
    data = mydb.query(sql, [context.geek])
    return data[0][0] > 0

def getMorgansPieChartsData(geek):
    import mydb
    sql1 = "select count(game), round(rating) from geekgames where geek = %s and owned = True and rating >= 0 group by round(rating)"
    data1 = mydb.query(sql1, [geek])
    sql2 = "select count(games.bggid), round(games.average) from geekgames inner join games on games.bggid = geekgames.game where geek = %s and geekgames.owned = True and average > 0 group by round(games.average)"
    data2 = mydb.query(sql2, [geek])
    sql3 = "select sum(quantity), round(rating) from geekgames inner join plays using (geek, game) where geek = %s and rating >= 0 group by round(rating)"
    data3 = mydb.query(sql3, [geek])
    sql4 = "select sum(quantity), round(rating) from geekgames inner join plays using (geek, game) where geek = %s and rating >= 0 and playDate > DATE_SUB(NOW(), INTERVAL 1 YEAR) group by round(rating)"
    data4 = mydb.query(sql4, [geek])
    return [data1, data2, data3, data4]

def getCrazyRecommendationsData(context):
    import library, mydb
    queries = {}
    queries["category"] = "select gameId, sum(n) from gameCategories, (select category c, count(category) n from gameCategories, geekgames where geek = %s and gameCategories.gameId = geekgames.game and rating >= 9 group by category) t1 where gameCategories.category = c group by gameId"
    queries["mechanic"] = "select gameId, sum(n) from gameMechanics, (select mechanic c, count(mechanic) n from gameMechanics, geekgames where geek = %s and gameMechanics.gameId = geekgames.game and rating >= 9 group by mechanic) t1 where gameMechanics.mechanic = c group by gameId"
    queries["designer"] = "select gameId, sum(n) from gameDesigners, (select designerId c, count(designerId) n from gameDesigners, geekgames where geek = %s and gameDesigners.gameId = geekgames.game and rating >= 9 group by designerId) t1 where gameDesigners.designerId = c group by gameId"
    queries["minplayers"] = "select bggid, sum(n) from games, (select minPlayers c, count(minPlayers) n from games, geekgames where geek = %s and games.bggid = geekgames.game and rating >= 9 group by minPlayers) t1 where games.minPlayers = c group by bggid"
    queries["maxplayers"] = "select bggid, sum(n) from games, (select maxPlayers c, count(maxPlayers) n from games, geekgames where geek = %s and games.bggid = geekgames.game and rating >= 9 group by maxPlayers) t1 where games.maxPlayers = c group by bggid"
    queries["playtime"] = "select bggid, sum(n) from games, (select playTime c, count(playTime) n from games, geekgames where geek = %s and games.bggid = geekgames.game and rating >= 9 group by playTime) t1 where games.playTime = c group by bggid"
    ratings = {}
    for (key, sql) in queries.items():
        data = mydb.query(sql, [context.geek])
        for (gid, n) in data:
            # weight the factors
            if key == "minplayers":
                n = n / 2
            elif key == "designer":
                n = n * 5
            elif key in ["category","mechanic"] and n > 50:
                n = 50
            if ratings.get(gid) is None:
                t = library.Thing()
                for k in queries.keys():
                    t.__dict__[k] = 0
                t.total = 0
                t.bggid = gid
                t.owned = 0
                t.rating = -1.0
                t.wish = 0
            else:
                t = ratings[gid]
            t.total = t.total + n
            t.__dict__[key] = n
            ratings[gid] = t
    rs = ratings.values()[:]
    rs.sort(lambda a,b: -cmp(a.total, b.total))
    collData = mydb.query("select game, owned, rating, wish from geekgames where geek = %s", [context.geek])
    for (gid, owned, rating, wish) in collData:
        t = ratings.get(gid)
        if t is None:
            continue
        t.owned = int(owned)
        t.rating = rating
        t.wish = wish
    expansions = mydb.query("select distinct expansion from expansions")
    expansions = [ x[0] for x in expansions ]
    books = mydb.query("select gameId from gameCategories where category = 'Book'")
    books = [x[0] for x in books]
    rs = [ r for r in rs if r.wish != 5 and r.bggid not in expansions and r.bggid not in books ]
    count = 0
    found = 0
    for r in rs:
        r.found = False
        count += 1
        if r.owned or r.rating > 0:
            continue
        r.found = True
        found += 1
        if found == 50:
            break
    rs = rs[:count]
    gids = [r.bggid for r in rs]
    games = context.substrate.getGames(gids)
    for r in rs:
        game = games[r.bggid]
        r.gameurl = game.url
        r.gamename = game.name
    context.substrate.addPlaysDataToGeekGames(rs)
    return rs

def getNumPlayersData(context):
    import library, mydb
    sqls = ["select geekgames.game, geekgames.rating, best%d, recommended%d from geekgames, numplayers where geekgames.geek = %s and geekgames.game = numplayers.game and best%d + recommended%d > notrec%d and geekgames.rating > 5 and geekgames.game not in (select gameId from gameCategories where category = 'Book' or category = 'Expansion for Base-game')" % (n+1, n+1, "%s", n+1, n+1, n+1) for n in range(7)]
    result = []
    games = []
    for sql in sqls:
        data = mydb.query(sql, [context.geek])
        result.append(data)
        for (gid, rating, best, rec) in data:
            if gid not in games:
                games.append(gid)
    gs = context.substrate.getGames(games)
    res2 = []
    players = 1
    for rs in result:
        r2 = []
        for (gid, rating, best, rec) in rs:
            g = gs[gid]
            mult = 1.0
            if players < g.minplayers or players > g.maxplayers:
                mult = 0.75
            t = library.Thing()
            (t.name, t.url) = (g.name, g.url)
            t.rating = rating
            t.sort = rating * mult
            r2.append(t)
            if best > rec:
                t.sort += 1.5
        r2.sort(lambda g1, g2: -cmp(g1.sort, g2.sort))
        res2.append(r2[:20])
        players += 1
    return res2

def getLeastWanted(context):
    import mydb
    sql = "select game, trade, max(playDate), datediff(now(), max(playDate)) / rating / rating, rating, datediff(now(), max(playDate)) from geekgames inner join plays using (geek, game) where geek = %s and rating > 0 and owned = True group by game order by 4 desc"
    data = mydb.query(sql, [context.geek])
    data = [ d for d in data if d[3] > 30 ]
    games = [ d[0] for d in data ]
    gs = context.substrate.getGames(games)
    result = []
    for (g, trade, lastPlay, x, rating, daysSince) in data:
        t = gs[g]
        if t.expansion or "Book" in t.categories:
            continue
        t.trade = trade
        t.lastPlay = lastPlay
        t.daysSince = daysSince
        t.rating = rating
        t.x = x
        result.append(t)
    return result

def getPlaysForYear(substrate, year):
    import library
    (startDate, endDate) = library.makeDateRange(year, None,  None)
    (plays, messages) = substrate.filterPlays(startDate, endDate)
    addGeekData(substrate.geek,  plays)
    return plays

def getStreaks(context):
    import library
    plays = getPlaysForYear(context.substrate, None)
    counts = library.Counts()
    for p in plays:
        d = library.parseDate(p.date)
        if d is not None:
            counts.add(d, p.count)
    plays = None
    result = []
    minPlays = 1
    while True:
        prevDate = None
        startDate = None
        dates = counts.keys()[:]
        dates.sort()
        streakLength = 0
        streaks = []
        for d in dates:
            if prevDate is None:
                # first streak
                startDate = d
                streakLength = 1
            elif library.consecutiveDays(prevDate, d):
                # streak continues
                streakLength += 1
            elif streakLength > 1:
                # streak is broken, new streak starts
                streaks.append((startDate, prevDate, streakLength))
                startDate = d
                streakLength = 1
            else:
                # previous was just a single day
                startDate = d
            prevDate = d
        if streakLength > 1:
            streaks.append((startDate, prevDate, streakLength))
        if len(streaks) == 0:
            break
        streaks.sort(lambda s1,s2: -cmp(s1[2], s2[2]))
        best = streaks[0]
        t = library.Thing()
        t.count = minPlays
        t.start = best[0]
        t.finish = best[1]
        t.length = best[2]
        result.append(t)
        minPlays += 1
        for key in counts.keys():
            if counts[key] < minPlays:
                del counts[key]
    return result

def getBestDays(context, year=None):
    import math, library
    plays = getPlaysForYear(context.substrate, year)
    dates = { p.date for p in plays }
    calcs = []
    for d in dates:
        ps = [ p for p in plays if p.date == d ]
        plays = [ p for p in plays if p.date != d ]
        if d is None:
            continue
        games = { p.game for p in ps }
        playDescs = []
        score = 0.0
        for g in games:
            q = 0
            r = -1
            for p in ps:
                if p.game == g:
                   q = q + p.count
                   r = p.rating
            t = library.Thing()
            t.plays = q
            t.name = g.name
            t.url = g.url
            playDescs.append(t)
            if q > 1.5:
                q = 1.5
            if r < 0:
                continue
            score += math.copysign(q * math.pow(math.copysign(r-5.0,  1),  1.75),  r - 5.0)
        calcs.append((d,  playDescs,  score))
    calcs.sort(lambda d1,  d2: -cmp(d1[2],  d2[2]))
    result = []
    for (d,  ps,  score) in calcs:
        t = library.Thing()
        t.plays = ps
        t.date = d
        t.score = score
        df = d.split("-")
        (t.year, t.month, t.day) = (df[0], df[1], df[2])
        result.append(t)
    return result

class DesignerPlaysData:
    def __init__(self, did, name):
        self.bggid = int(did)
        self.name = name
        self.totalPlays = 0
        self.totalCount = 0
        self.baseGamePlays = 0
        self.baseGameCount = 0
        self.expansionPlays = 0
        self.expansionCount = 0
        self.baseGames = []
        self.expansions = []
        self.games = []

    def toMap(self):
        result = {}
        result["bggid"] = self.bggid
        result["name"] = self.name
        result["totalPlays"] = self.totalPlays
        result["totalCount"] = self.totalCount
        result["baseGamePlays"] = self.baseGamePlays
        result["baseGameCount"] = self.baseGameCount
        result["expansionPlays"] = self.expansionPlays
        result["expansionCount"] = self.expansionCount
        result["baseGames"] = self.baseGames
        result["expansions"] = self.expansions
        result["games"] = self.games
        return result

def getDimesByDesigner(context, year=None):
    import library, mydb
    range = []
    if year is not None:
        range = [year]
    (plays, messages, year, month, day, args) = context.substrate.getPlaysForDescribedRange(range)
    gids = []
    for p in plays:
        if p.game.bggid not in gids:
            gids.append(p.game.bggid)
            p.game.plays = 0
        for e in p.expansions:
            if e.bggid not in gids:
                gids.append(e.bggid)
                e.plays = 0
    if len(gids) == 0:
        return []
    sql = "select games.bggid, designers.name, designers.bggid from designers, gameDesigners, games where designers.bggid = gameDesigners.designerId and " + \
          "gameDesigners.gameId = games.bggid and " + library.inlist("games.bggid", gids)
    designerData = mydb.query(sql, [])
    designers = {}
    designersByGame = library.DictOfLists()
    for (gid,  dname,  did) in designerData:
        if designers.get(did) is None:
            designers[did] = DesignerPlaysData(did, dname)
        d = designers[did]
        designersByGame.add(gid, d)
    for p in plays:
        p.game.plays = p.game.plays + p.count
        for d in designersByGame[p.game.bggid]:
            d.baseGamePlays = d.baseGamePlays + p.count
            if p.game not in d.games:
                d.games.append(p.game)
                d.baseGames.append(p.game)
        for e in p.expansions:
            e.plays = e.plays + p.count
            for d in designersByGame[e.bggid]:
                d.expansionPlays = d.expansionPlays + p.count
                if e not in d.games:
                    d.games.append(e)
                    d.expansions.append(e)
    for d in designers.values():
        d.totalPlays = d.baseGamePlays + d.expansionPlays
        d.baseGameCount = len(d.baseGames)
        d.expansionCount = len(d.expansions)
        d.totalCount = d.baseGameCount + d.expansionCount
        d.games.sort(lambda g1, g2: -cmp(g1.plays, g2.plays))
    result = [ d for d in designers.values() if d.totalPlays >= 10 ]
    result.sort(lambda d1, d2: -cmp(d1.totalPlays, d2.totalPlays))
    return result

def getPlaysRecordedYears(context):
    import mydb
    sql = "select distinct(year(playDate)) from plays where geek = %s"
    years = mydb.query(sql, [context.geek])
    years = [ int(row[0]) for row in years ]
    return years

def getNickelAndDime(context, year):
    import library
    (plays, messages, year, month, day, args) = context.substrate.getPlaysForDescribedRange([str(year)])
    plays = collatePlays(plays)
    data = [ p for p in plays if p.count >= 3 ]
    data.sort(lambda p1, p2: -cmp(p1.count, p2.count))
    result = library.Thing()
    result.dollars = []
    result.halfdollars = []
    result.quarters = []
    result.dimes = []
    result.nickels = []
    result.nearly = []
    for p in data:
        g = p.game
        g.plays = p.count
        if g.plays >= 100:
            result.dollars.append(g)
        elif g.plays >= 50:
            result.halfdollars.append(g)
        elif g.plays >= 25:
            result.quarters.append(g)
        elif g.plays >= 10:
            result.dimes.append(g)
        elif g.plays >= 5:
            result.nickels.append(g)
        else:
            result.nearly.append(g)
    return result

def getPlayedLastYearNotThis(context, year):
    import mydb
    sql = "select game, q from (select game, sum(quantity) q from plays where geek = %s and year(playDate) = %s group by game) t1 where q >= 2 and game not in (select game from plays where geek = %s and year(playDate) = %s) order by 2 desc"
    data = mydb.query(sql, [context.geek, year-1, context.geek, year])
    gids = [ d[0] for d in data ]
    gs = context.substrate.getGames(gids)
    result = []
    for (gid, count) in data:
        g = gs[gid]
        g.plays = count
        result.append(g)
    return result

def getPlaysByYearData(context):
    import library
    result = []
    opts = context.options.pbm
    playData = context.substrate.getPlaysForDescribedRange([])[0]
    years = {}
    games = []
    for play in playData:
        if not play.year:
            continue
        elif not play.year in years:
            years[play.year] = []
        years[play.year].append(play)
        if play.game not in games:
            games.append(play.game)
        for g in play.expansions:
            if g not in games:
                games.append(g)
    # calculate year-to-date stuff
    playedSoFar = set()
    sortedYears = years.keys()[:]
    sortedYears.sort()
    for y in sortedYears:
        yPlays = years[y]
        playTime = 0
        totalPlays = 0
        newGames = 0
        dollars = 0
        quarters = 0
        dimes = 0
        nickels = 0
        playsByGame = {}
        daysPlayedOn = []
        for play in yPlays:
            day = "%4d-%02d-%02d" % (play.year, play.month, play.day)
            if not day in daysPlayedOn:
                daysPlayedOn.append(day)
            playTime += play.count * play.game.playtime
            totalPlays += play.count
            if play.game not in playsByGame:
                playsByGame[play.game] = []
            playsByGame[play.game].append(play)
            if not play.game in playedSoFar:
                newGames += 1
                playedSoFar.add(play.game)
        for (game, plays) in playsByGame.items():
            gp = sum([p.count for p in plays])
            if gp >= 100:
                dollars += 1
            elif gp >= 25:
                quarters += 1
            elif gp >= 10:
                dimes += 1
            elif gp >= 5:
                nickels += 1
        t = library.Thing()
        t.year = y
        t.playHours = int((playTime + 30) / 60)
        t.totalPlays = totalPlays
        t.distinctGames = len(playsByGame)
        t.newGames = newGames
        t.dollars = dollars
        t.quarters = quarters
        t.dimes = dimes
        t.nickels = nickels
        t.daysPlayedOn = len(daysPlayedOn)
        result.append(t)
    result.reverse()
    return result

def getRatingByRanking(context):
    import library, mydb
    from imggen import ALDIES_COLOURS
    opts = library.Thing()
    opts.excludeTrades = False
    opts.excludeExpansions = False
    geekgames = context.substrate.getAllRatedGames(opts)
    sql = "select bggid, name, rank from games where usersRated >= 30 order by 3 asc"
    gdata = mydb.query(sql)
    games = {}
    index = {}
    highestRank = -1
    for (gid, name, rank) in gdata:
        t = library.Thing()
        t.name = name
        t.rank = rank
        games[gid] = t
        index[rank] = t
        if rank > highestRank:
            highestRank = rank
        t.colour = "#ffffff"
        t.rating = None
    for gg in geekgames:
        g = games.get(gg.game.bggid)
        if g is None:
            continue
        g.rating = gg.rating
        g.colour = ALDIES_COLOURS[int(g.rating-1)]
    result = []
    r = 1
    rindex = {}
    while r <= highestRank:
        row = library.Thing()
        row.count = 0
        row.sum = 0.0
        row.average = 0.0
        row.elements = 0
        row.base = r
        row.data = []
        for i in range(100):
            t = index.get(row.base + i)
            if t is not None:
                row.data.append(t)
            else:
                row.data.append(None)
        result.append(row)
        rindex[int(r/100)] = row
        r += 100
    for g in games.values():
        if g.rank <= 0:
            continue
        row = rindex[int((g.rank-1)/100)]
        row.elements += 1
        if g.rating is not None and g.rating > 0:
            row.count += 1
            row.sum = row.sum + g.rating
            row.average = int(row.sum * 10.0 / row.count) / 10.0
    return result

def getPlaysByRanking(context):
    import library, mydb
    opts = library.Thing()
    opts.excludeTrades = False
    opts.excludeExpansions = False
    sql = "select bggid, name, rank from games where usersRated >= 30 order by 3 asc"
    gdata = mydb.query(sql)
    games = {}
    index = {}
    highestRank = -1
    for (gid, name, rank) in gdata:
        t = library.Thing()
        t.name = name
        t.rank = rank
        games[gid] = t
        index[rank] = t
        if rank > highestRank:
            highestRank = rank
        t.colour = "#ffffff"
        t.plays = 0
    gs = context.substrate.getGeekGames(games.keys())
    for gg in gs:
        g = games.get(gg.game.bggid)
        g.plays = gg.plays
        if g.plays == 0:
            g.colour = library.WHITE
        elif g.plays == 1:
            g.colour = library.RED
        elif g.plays < 3:
            g.colour = library.ORANGE
        elif g.plays < 5:
            g.colour = library.YELLOW
        elif g.plays < 10:
            g.colour = library.YELLOWGREEN
        elif g.plays < 25:
            g.colour = library.GREEN
        else:
            g.colour = library.DARKGREEN
        g.name += " %d plays" % g.plays
    result = []
    r = 1
    rindex = {}
    while r < highestRank:
        row = library.Thing()
        row.count = 0
        row.plays = 0
        row.base = r
        row.data = []
        for i in range(100):
            t = index.get(row.base + i)
            if t is not None:
                row.data.append(t)
            else:
                row.data.append(None)
        result.append(row)
        rindex[int(r/100)] = row
        r += 100
    for g in games.values():
        if g.rank <= 0:
            continue
        try:
            row = rindex[int((g.rank-1)/100)]
            row.count += 1
            row.plays = row.plays + g.plays
        except KeyError:
            # why does this happen?
            continue
    return result

def getCategoriesToGraph(context):
    import mydb
    sql = "select category from (select category, count(category) c from geekgames join gameCategories on gameId = game, games where geek = %s and rating > 0 and bggid = game group by category) t where c >= 30"
    data = mydb.query(sql, [context.geek])
    return [ d[0] for d in data ]

def getMechanicsToGraph(context):
    import mydb
    sql = "select mechanic from (select mechanic, count(mechanic) c from geekgames join gameMechanics on gameId = game, games where geek = %s and rating > 0 and bggid = game group by mechanic) t where c >= 30"
    data = mydb.query(sql, [context.geek])
    return [ d[0] for d in data ]

def getDesignersToGraph(context):
    import library, mydb
    sql = "select designerId, name from (select designerId, count(designerId) c from geekgames join gameDesigners on gameId = game, games where geek = %s and rating > 0 and bggid = game group by designerId) t, designers where designerId = bggid and c >= 10"
    data = mydb.query(sql, [context.geek])
    result = []
    for (id, name) in data:
        t = library.Thing()
        (t.id, t.name) = (id, name)
        result.append(t)
    return result

def getPublishersToGraph(context):
    import library, mydb
    sql = "select publisherId, name from (select publisherId, count(publisherId) c from geekgames join gamePublishers on gameId = game, games where geek = %s and rating > 0 and bggid = game group by publisherId) t, publishers where c >= 30 and publisherId = bggid"
    data = mydb.query(sql, [context.geek])
    result = []
    for (id, name) in data:
        t = library.Thing()
        (t.id, t.name) = (id, name)
        result.append(t)
    return result

def getSeriesData(context):
    import library, mydb
    sql = "select series.name, game, rating, comment, want, owned, wish, trade from series left outer join (select * from geekgames where geek = %s) t using (game)"
    data = mydb.query(sql, [context.geek])
    gids = [ d[1] for d in data ]
    games = context.substrate.getGames(gids)
    bySeries = {}
    for (sname, gid, rating, comment, want, owned, wish, trade) in data:
        g = games[gid]
        if g.rank <= 0:
            g.rank = 0
        if rating <= 0:
            rating = 0
        g.rating = rating
        if comment == "&nbsp;":
            comment = ""
        g.comment = comment
        g.want = want
        g.owned = owned
        g.wish = wish
        g.trade = trade
        # add id that addPlaysDataToGeekGames will be expecting
        g.bggid = gid
        s = bySeries.get(sname)
        if s is None:
            s = [g]
            bySeries[sname] = s
        else:
            s.append(g)
    context.substrate.addPlaysDataToGeekGames(games.values())
    result = []
    for (k, v) in bySeries.items():
        t = library.Thing()
        t.name = k
        t.games = v
        tot = 0
        count = 0
        owned = 0
        for g in t.games:
            tot = tot + g.rating
            if g.rating > 0:
                count += 1
            if g.owned:
                owned += 1
        t.total = tot
        t.count = count
        t.owned = owned
        t.mean = 0.0
        if count > 0:
            t.mean = int (100.0 * tot / count) / 100.0
        result.append(t)
    result.sort(lambda s1, s2: cmp(s1.name, s2.name))
    return result

def getUnusualData(context):
    import mydb
    sql = "select game, usersRated + usersOwned from geekgames, games where game = bggid and geek = %s and owned order by 2 asc"
    data = mydb.query(sql, [context.geek])[:50]
    gids = [ d[0] for d in data ]
    games = context.substrate.getGames(gids)
    result = [ games[gid] for (gid, v) in data ]
    return result

DESIGNER_URL = "http://www.boardgamegeek.com/boardgamedesigner/%d"
PUBLISHER_URL = "http://www.boardgamegeek.com/boardgamepublisher/%d"

def getNewCatRow(key, typ):
    import library
    t = library.Thing()
    t.key = key
    t.owned = 0
    t.avgOwned = 0
    t.name = str(key)
    t.rating = 0
    t.count = 0
    t.favid = 0
    t.plays = 0
    t.whitmore = 0
    t.whitmoreNoExp = 0
    t.collection = []
    if typ == "designer":
        t.url = DESIGNER_URL % key
    elif typ == "publisher":
        t.url = PUBLISHER_URL % key
    else:
        t.url = None
    return t

def getCatMecData(context, typ):
    import mydb
    if typ == "category":
        tab = "category from gameCategories"
        where = "category"
    elif typ == "mechanic":
        tab = "mechanic from gameMechanics"
        where = "mechanic"
    elif typ == "designer":
        tab = "designerId from gameDesigners"
        where = "designerId"
    else:
        tab = "publisherId from gamePublishers"
        where = "publisherId"
    table = tab.split()[-1]
    sql = "select sum(owned), %s join geekgames on gameId = game where geek = %s group by %s" % (tab, "%s", where)
    byKey = {}
    data = mydb.query(sql, [context.geek])
    for (owned, key) in data:
        owned = int(owned)
        t = getNewCatRow(key, typ)
        t.owned = owned
        byKey[key] = t
    if typ in ["designer", "publisher"]:
        inlist = "(" + ", ".join([str(k) for k in byKey.keys()]) + ")"
        if typ == "designer":
            sql = "select name, bggid from designers where bggid in %s"
        elif typ == "publisher":
            sql = "select name, bggid from publishers where bggid in %s"
        names = mydb.query(sql % inlist)
        for (name, id) in names:
            byKey[id].name = name
    sql = "select avg(rating), count(rating), %s join geekgames on gameId = game where geek = %s and rating > 0 group by %s" % (tab, "%s", where)
    data = mydb.query(sql, [context.geek])
    for (avg, count, key) in data:
        byKey[key].rating = int(avg * 10) / 10.0
        byKey[key].count = int(count)
    sql = "select avg(rating), %s join geekgames on gameId = game where geek = %s and owned and rating > 0 group by %s" % (tab, "%s", where)
    data = mydb.query(sql, [context.geek])
    for (avg, key) in data:
        byKey[key].avgOwned = int(avg * 10) / 10.0
    sql = "select sum(quantity), %s from (select quantity, game from plays where geek = %s) t1 join %s on game = gameId group by %s" % (where, "%s", table, where)
    data = mydb.query(sql, [context.geek])
    for (plays, key) in data:
        if byKey.get(key) is None:
            t = getNewCatRow(key, typ)
            byKey[key] = t
        byKey[key].plays = int(plays)
    sql = "select %s, sum(p) / 60 from (select playTime * sum(quantity) p, game from plays, games where geek = %s and game = bggid group by game) t1 join %s on game = gameId group by %s" % (where, "%s", table, where)
    data = mydb.query(sql, [context.geek])
    for (key, hours) in data:
        byKey[key].hoursPlayed = int(hours * 10) / 10.0
    sql = "select sum(w), %s from (select case when rating = 10 then 7 when rating >= 9 then 5 when rating >= 8 then 3 when rating >= 7 then 1 else 0 end w, game from geekgames where geek = %s) t1 join %s on gameId = game group by %s" % (where, "%s", table, where)
    data = mydb.query(sql, [context.geek])
    for (whitmore, key) in data:
        byKey[key].whitmore = whitmore
    sql = "select sum(w), %s from (select case when rating = 10 then 7 when rating >= 9 then 5 when rating >= 8 then 3 when rating >= 7 then 1 else 0 end w, game from geekgames where geek = %s) t1, games, %s where t1.game = games.bggid and %s.gameId = t1.game and t1.game not in (select expansion from expansions) group by %s order by 1 desc" % (where, "%s", table, table, where)
    data = mydb.query(sql, [context.geek])
    for (whitmore, key) in data:
        byKey[key].whitmoreNoExp = whitmore
    sql = "select %s, gameId from (select max(rating) m, %s join geekgames on gameId = game where geek = %s and rating > 0 group by %s) t1 join (select gameId, rating r, %s join geekgames on gameId = game where geek = %s and rating > 0) t2 using (%s) where r = m" % (where, tab, "%s", where, tab, "%s", where)
    data = mydb.query(sql, [context.geek, context.geek])
    gids = set()
    for (key, gid) in data:
        byKey[key].favid = gid
        gids.add(gid)
    #
    sql = "select game, %s join geekgames on gameId = game where geek = %s and owned" % (tab, "%s")
    data = mydb.query(sql, [context.geek])
    for (gid, key) in data:
        gids.add(gid)
        byKey[key].collection.append(gid)
    #
    games = context.substrate.getGames(gids)
    for t in byKey.values()[:]:
        if t.favid:
            t.favgame = games[t.favid]
        t.collection = [ games[gid] for gid in t.collection ]
    result = byKey.values()[:]
    result = [ r for r in result if r.rating > 0 or r.owned > 0 ]
    result.sort(lambda r1, r2: cmp(r1.name, r2.name))
    return result

def getNormalisedRankingsData():
    import library, mydb
    sql = "select geek, count(geek) from geekgames where rating > 0 group by geek"
    data = mydb.query(sql)
    totals = {}
    for (geek, count) in data:
        t = library.Thing()
        t.count = count
        t.geek = geek
        t.soFar = 0
        t.rankAs = 0
        t.lastRating = None
        totals[geek] = t
    pointsForGames = {}
    sql = "select geek, game, rating from geekgames where rating > 0 order by rating desc"
    data = mydb.query(sql)
    for (geek, gid, rating) in data:
        t = totals[geek]
        if rating != t.lastRating:
            t.rankAs = t.soFar
            t.lastRating = rating
        t.soFar += 1
        score = 1.0 * (t.count - t.rankAs) / t.count
        g = pointsForGames.get(gid)
        if g is None:
            g = library.Thing()
            pointsForGames[gid] = g
            g.bggid = gid
            g.score = 0
            g.count = 0
        g.score += score
        g.count += 1
    gs = pointsForGames.values()[:]
    gs.sort(lambda g1, g2: -cmp(g1.score, g2.score))
    rank = 1
    for g in gs:
        g.normrank = rank
        rank += 1
    return pointsForGames

def getNormalisedRankingsDataForGames(bggids):
    if len(bggids) == 0:
        return {}
    import library, mydb
    sql = "select geek, count(geek) from geekgames where rating > 0 and game in %s group by geek"
    data = mydb.query(sql, [bggids])
    totals = {}
    for (geek, count) in data:
        t = library.Thing()
        t.count = count
        t.geek = geek
        t.soFar = 0
        t.rankAs = 0
        t.lastRating = None
        totals[geek] = t
    pointsForGames = {}
    sql = "select geek, game, rating from geekgames where rating > 0 and game in %s order by rating desc"
    data = mydb.query(sql, [bggids])
    for (geek, gid, rating) in data:
        t = totals[geek]
        if rating != t.lastRating:
            t.rankAs = t.soFar
            t.lastRating = rating
        t.soFar += 1
        score = 1.0 * (t.count - t.rankAs) / t.count
        g = pointsForGames.get(gid)
        if g is None:
            g = library.Thing()
            pointsForGames[gid] = g
            g.bggid = gid
            g.score = 0
            g.count = 0
        g.score += score
        g.count += 1
    gs = pointsForGames.values()[:]
    gs.sort(lambda g1, g2: -cmp(g1.score, g2.score))
    rank = 1
    for g in gs:
        g.normrank = rank
        rank += 1
    return pointsForGames

def getTradeData(context):
    import library, mydb
    sql = "select country from users where geek = %s"
    data = mydb.query(sql, [context.geek])
    if data is None or len(data) == 0 or len(data[0]) == 0 or data[0][0] is None:
        return ("Unknown Country '" + str(data) + "'", [context.geek], [], [], [])
    country = data[0][0]
    if country.startswith("United") and country.endswith("States"):
        return ("This functionality is not available for your country because it puts too much load on the server.", [context.geek], [], [], [])
    sql = "select geek from users where country = %s"
    data = mydb.query(sql, [country])
    geeks = []
    usernames = []
    byGeek = {}
    for row in data:
        t = library.Thing()
        t.username = row[0]
        t.want = 0
        t.trade = 0
        t.sell = 0
        usernames.append(t.username)
        geeks.append(t)
        byGeek[t.username.lower()] = t
        t.forTrade = []
        t.wanted = []
        t.owned = []
        t.wish5 = []
        t.selling = []
    try:
        meGeek = byGeek[context.geek.lower()]
    except KeyError:
        return ("Unknown Country '" + str(country) + "'", [meGeek], [], [], [])
    sql = "select geek, game, owned, want, wish, trade, wanttobuy from geekgames where %s" % library.strinlist("geek", usernames)
    data = mydb.query(sql)
    sql = "select geek, gameid, itemid from market where %s" % library.strinlist("geek", usernames)
    marketData = mydb.query(sql)
    ids = []
    for (geek, id, owned, want, wish, trade, wanttobuy) in data:
        if id not in ids:
            ids.append(id)
    for (geek, id, itemid) in marketData:
        if id not in ids:
            ids.append(id)
    games = context.substrate.getGames(ids)
    for g in games.values():
        g.wanting = []
        g.notwanting = []
        g.selling = []
        g.exciting = False
    for (geek, id, owned, want, wish, trade, wanttobuy) in data:
        game = games[id]
        t = byGeek[geek.lower()]
        if owned:
            t.owned.append(game)
        if owned and trade:
            t.trade += 1
            t.forTrade.append(game)
            game.notwanting.append(t)
        if want or wish in [1,2,3,4] or wanttobuy:
            t.want += 1
            t.wanted.append(game)
            game.wanting.append(t)
        if wish == 5:
            t.wish5.append(game)
    for (geek, id, itemid) in marketData:
        game = games.get(id)
        if game is None:
            continue
        t = byGeek[str(geek).lower()]
        t.sell += 1
        t.selling.append(game)
        sale = library.Thing()
        sale.geek = geek
        sale.itemid = itemid
        game.selling.append(sale)
    geeks = [ g for g in geeks if g.want > 0 or g.trade > 0 or g.sell > 0 ]
    geeks.sort(lambda g1, g2: cmp(g1.username.lower(), g2.username.lower()))
    for g in geeks:
        if g == meGeek:
            g.tooltip = ""
            g.tooltip2 = ""
        else:
            g.tooltip = ", ".join([game.name for game in g.wanted if game in meGeek.owned])
            g.tooltip2 = ", ".join([game.name for game in g.forTrade])
    interestingGames = []
    mostWantedGames = []
    leastWantedGames = []
    for g in games.values():
        g.howManyWant = len(g.wanting)
        g.howManyDontWant = len(g.notwanting)
        if g.howManyWant > 1:
            mostWantedGames.append(g)
        if g.howManyDontWant > 1:
            leastWantedGames.append(g)
        if g in meGeek.wish5 and g not in meGeek.owned and g not in meGeek.wanted:
            continue
        if len(g.wanting) == 0 and len(g.notwanting) == 0:
            continue
        if g not in meGeek.forTrade and len(g.notwanting) == 0:
            continue
        g.exciting = (meGeek in g.wanting) or (meGeek in g.notwanting)
        interestingGames.append(g)
    interestingGames.sort(lambda g1, g2: cmp(g1.name.lower(), g2.name.lower()))
    mostWantedGames.sort(lambda g1, g2: -cmp(g1.howManyWant, g2.howManyWant))
    leastWantedGames.sort(lambda g1, g2: -cmp(g1.howManyDontWant, g2.howManyDontWant))
    return country, geeks, interestingGames, mostWantedGames[:30], leastWantedGames[:30]

def getTemporalHotnessMonthData(context):
    import library, datetime
    plays = context.substrate.filterPlays(None, None)[0]
    years = getGeekYears(context.geek)
    today = datetime.date.today()
    if today.year not in years:
        years.append(today.year)
    result = []
    values = []
    totals = []
    monthTotals = library.Counts()
    tot = 0
    for y in years:
        t = library.Thing(str(y))
        t.year = y
        counts = library.Counts()
        result.append(t)
        for p in plays:
            if p.year == y:
                counts.add(p.month, p.count)
        t.months = []
        t.count = 0
        for i in range(12):
            m = library.Thing()
            m.count = counts[i+1]
            t.count = t.count + m.count
            t.months.append(m)
            values.append(m.count)
            monthTotals.add(i,m.count)
        totals.append(t.count)
        tot += t.count
    t = library.Thing("Total")
    t.count = tot
    t.months = []
    counts = []
    for i in range(12):
        m = library.Thing()
        m.count = monthTotals[i]
        counts.append(m.count)
        t.months.append(m)
    (avg, sd) = stddev(counts)
    applyHotnessClasses(t.months, avg, sd)
    while len(values) > 0 and values[0] == 0:
        values = values[1:]
    while len(values) > 0 and values[-1] == 0:
        values = values[:-1]
    if len(values) > 0:
        (avg, sd) = stddev(values)
        for year in result:
            applyHotnessClasses(year.months, avg, sd)
    while len(totals) > 0 and totals[-1] == 0:
        totals = totals[:-1]
    if len(totals) > 0:
        (avg, sd) = stddev(totals)
        applyHotnessClasses(result, avg, sd)
    result.append(t)
    return result

def getTemporalHotnessDayData(context):
    import library, datetime
    plays = context.substrate.filterPlays(None, None)[0]
    years = getGeekYears(context.geek)
    today = datetime.date.today()
    if today.year not in years:
        years.append(today.year)
    dayTotals = library.Counts()
    yearTotals = library.Counts()
    dayYear = library.DictOfCounts()
    for p in plays:
        if p.year not in years:
            continue
        dow = p.dt.weekday()
        dayTotals.add(dow, p.count)
        yearTotals.add(p.year, p.count)
        dayYear.add(p.year, dow, p.count)
    result = []
    values = []
    for y in years:
        t = library.Thing(str(y))
        t.data = []
        t.count = yearTotals[y]
        result.append(t)
        for dow in range(7):
            d = library.Thing()
            d.count = dayYear.getCount(y, dow)
            values.append(d.count)
            t.data.append(d)
    (avg, sd) = stddev([y.count for y in result])
    applyHotnessClasses(result, avg, sd)
    (avg, sd) = stddev(values)
    for year in result:
        applyHotnessClasses(year.data, avg, sd)
    all = library.Thing("Total")
    all.count = sum([y.count for y in result])
    all.data = []
    for dow in range(7):
        t = library.Thing()
        t.count = dayTotals[dow]
        all.data.append(t)
    (avg, sd) = stddev([t.count for t in all.data])
    applyHotnessClasses(all.data, avg, sd)
    result.append(all)
    return result

def getTemporalHotnessDateData(context):
    import library
    plays = context.substrate.filterPlays(None, None)[0]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    result = []
    values = []
    totals = []
    for m in range(len(months)):
        t = library.Thing(str(months[m]))
        t.index = m+1
        t.name = months[m]
        t.data = [ library.Thing() for d in range(31) ]
        result.append(t)
    counts = library.DictOfCounts()
    dateCounts = library.Counts()
    tot = 0
    for p in plays:
        counts.add(p.month, p.day, p.count)
        dateCounts.add(p.day, p.count)
    for t in result:
        t.count = 0
        for d in range(len(t.data)):
            n = counts.getCount(t.index, d+1)
            t.data[d].count = n
            values.append(n)
            t.count = t.count + n
        totals.append(t.count)
        tot += t.count
    all = library.Thing("Total")
    all.count = tot
    all.data = []
    for i in range(31):
        t = library.Thing()
        t.count = dateCounts[i+1]
        all.data.append(t)
    counts = [ t.count for t in all.data ]
    (avg, sd) = stddev(counts)
    applyHotnessClasses(all.data, avg, sd)
    while len(values) > 0 and values[0] == 0:
        values = values[1:]
    while len(values) > 0 and values[-1] == 0:
        values = values[:-1]
    (avg, sd) = stddev(values)
    for t in result:
        for d in t.data:
            applyHotnessClasses(t.data, avg, sd)
    (avg, sd) = stddev(totals)
    applyHotnessClasses(result, avg, sd)
    result.append(all)
    return result

def applyHotnessClasses(values, avg, sd):
    for m in values:
        m.cssClass = "class3"
        if m.count == 0:
            m.cssClass = "class0"
        elif m.count < avg - sd/2:
            if m.count < avg - sd:
                m.cssClass = "class1"
            else:
                m.cssClass = "class2"
        elif m.count > avg + sd/2:
            if m.count > avg + sd:
                m.cssClass = "class5"
            else:
                m.cssClass = "class4"

def average(s):
    return sum(s) * 1.0 / len(s)

def variance(s, avg):
    return map(lambda x: (x - avg)**2, s)

def stddev(s):
    import math
    avg = average(s)
    v = variance(s, avg)
    return (avg, math.sqrt(average(v)))
