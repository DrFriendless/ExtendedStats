import generate, imggen, webserver_factory
webserver = webserver_factory.get()

POGO_SELECTOR = "/owned/books/minus/\"Owned\""

class BadUrlException(Exception):
    pass

class Options(object):
    def __init__(self, request):
        import features, library
        self.consistencyMonths = 96
        self.pogo = library.Thing()
        self.upsideDownRbpy = (webserver.get_cookie(request, "rbpyUpsideDown") == "True")
        self.upsideDownObpy = (webserver.get_cookie(request, "obpyUpsideDown") == "True")
        self.upsideDownPbpy = (webserver.get_cookie(request, "pbpyUpsideDown") == "True")
        self.pogo.excludeExpansions = (webserver.get_cookie(request, "pogoExpansions") == "True")
        self.pogo.excludeTrades = (webserver.get_cookie(request, "pogoTrades") == "True")
        self.fave = library.Thing()
        self.fave.excludeExpansions = (webserver.get_cookie(request, "faveExpansions") == "True")
        self.fave.excludeTrades = (webserver.get_cookie(request, "faveTrades") == "True")
        self.obpy = library.Thing()
        self.obpy.excludeExpansions = (webserver.get_cookie(request, "obpyExpansions") == "True")
        self.obpy.excludeTrades = (webserver.get_cookie(request, "obpyTrades") == "True")
        self.pbm = library.Thing()
        self.pbm.excludeExpansions = (webserver.get_cookie(request, "pbmExpansions") == "True")
        self.pbm.excludeTrades = (webserver.get_cookie(request, "pbmTrades") == "True")
        self.pbm.timelineHeight = 400
        self.pbm.timelineWidth = 30000
        self.playrate = library.Thing()
        self.playrate.excludeExpansions = (webserver.get_cookie(request, "playrateExpansions") == "True")
        self.playrate.excludeTrades = (webserver.get_cookie(request, "playrateTrades") == "True")
        self.playrate.excludeUnrated = (webserver.get_cookie(request, "playrateUnrated") == "True")
        self.user = library.Thing()
        for feature in features.FEATURES:
            key = feature.name
            self.user.__dict__["include" + key] = (webserver.get_cookie(request, "user" + key) == "True")
        if webserver.get_cookie(request, "timelineHeight"):
            self.pbm.timelineHeight = int(webserver.get_cookie(request, "timelineHeight"))
        if webserver.get_cookie(request, "timelineWidth"):
            self.pbm.timelineWidth = int(webserver.get_cookie(request, "timelineWidth"))

    def __str__(self):
        return "Options[pogo[%s %s] fave[%s %s] obpy[%s %s] pbm[%d %d %s %s] playrate[%s %s %s] User Tab[%s]" % (`self.pogo.excludeExpansions`, `self.pogo.excludeTrades`,
                                                                                                                 `self.fave.excludeExpansions`,  `self.fave.excludeTrades`, `self.obpy.excludeExpansions`,  `self.obpy.excludeTrades`,
                                                                                                                 self.pbm.timelineHeight, self.pbm.timelineWidth, `self.pbm.excludeExpansions`, `self.pbm.excludeTrades`,
                                                                                                                 `self.playrate.excludeExpansions`, `self.playrate.excludeTrades`, `self.playrate.excludeUnrated`, `self.user.__dict__`)

class OptimisationContext(object):
    def __init__(self, geek, options, ispec):
        # options are all the options from the HTTP request
        import substrate
        self.geek = geek
        self.substrate = substrate.Substrate(geek, self)
        self.options = options
        self.imageSpec = ispec
        self.pbm = None
        self.byGeek = {}

    def getGeekContext(self, geek):
        if self.geek == geek:
            return self
        if self.byGeek.get(geek) is None:
            self.byGeek[geek] = OptimisationContext(geek, None, None)
        return self.byGeek[geek]

def interpretRequest(request, param):
    """look at the request and set up our context objects from it"""
    import library
    from imgviews import ImageSpecs
    ispec = ImageSpecs(request)
    options = Options(request)
    username = library.checkGeek(param, request)
    return OptimisationContext(username, options, ispec)

def interpretRequestAndSelector(request, param, default):
    import selectors
    if "/" in param:
        fields = param.split("/")
    else:
        fields = [ param ]
    context = interpretRequest(request, fields[0])
    fields = fields[1:]
    if len(fields) == 0:
        fields = default.split("/")
    selector = selectors.getSelectorFromFields(fields)
    return context, selector


def interpretRequestAndSelectorChain(request, param, default):
    import selectors
    if "/" in param:
        fields = param.split("/")
    else:
        raise BadUrlException("expected at least a user and a selector")
    context = interpretRequest(request, fields[0])
    fields = fields[1:]
    if len(fields) == 0:
        fields = default.split("/")
    selector = selectors.getSelectorsFromFields(fields)
    return context, selector


def interpretRequestAndSelectors(request, param, default):
    import selectors
    if "/" in param:
        fields = param.split("/")
    else:
        raise BadUrlException("expected at least a user and a tab index")
    context = interpretRequest(request, fields[0])
    try:
        index = int(fields[-1])
    except ValueError:
        raise BadUrlException("URL must end in a tab index")
    fields = fields[1:-1]
    if len(fields) == 0:
        fields = default.split("/")
    selector = selectors.getSelectorsFromFields(fields)
    return context, selector, index, "/".join(fields)

def interpretRequestAndParams(request, param):
    if "/" in param:
        fields = param.split("/")
    else:
        fields = [ param ]
    context = interpretRequest(request, fields[0])
    return context, fields[1:]

def manageCollections(request, param):
    import game_collections, library
    try:
        context = interpretRequest(request, param)
        username = context.geek
        colls = context.substrate.getCollections().values()[:]
        colls.sort(lambda c1, c2: cmp(c1.index, c2.index))
        newIndex = game_collections.getNextCollectionIndex(context)
        return webserver.render("stats/collections.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def viewSelections(request, param):
    import features, library, generate
    features = [ features.GenericTable, features.PogoTable ]
    all = {}
    try:
        (context, selectors, index, fragment) = interpretRequestAndSelectors(request, param, "owned")
        opts = library.Thing()
        opts.excludeExpansions = False
        opts.excludeTrades = False
        if index > len(selectors):
            raise BadUrlException("tab index exceeds number of tabs")
        if index <= 0:
            raise BadUrlException("tab indexes start at 1")
        tabs = []
        contents = []
        n = 1
        all = {}
        for s in selectors:
            tab = library.Thing()
            tab.name = s.name
            tab.index = n
            tab.selected = (index == n)
            tab.games = s.getGames(context, opts)
            if n == index:
                for f in features:
                    ff = f(s)
                    values = ff.generate(context)
                    if values is not None:
                        all.update(values)
                        contents.append(ff)
            tabs.append(tab)
            n += 1
        generate.addCollectionSummary(context, tabs)
        if selectors.columns is not None:
            visible = ",".join(selectors.columns)
        else:
            visible = "Name,Rating,Plays"
        all.update({"tabs" : tabs, "contents" : contents, "tab" : tabs[index-1], "username" : context.geek,
                    "tabs" : tabs, "fragment" : fragment, "visibleColumns" : visible})
        return webserver.render("stats/viewSelections.html", all, request)
    except BadUrlException, mesg:
        import selectors
        context = interpretRequest(request, param.split("/")[0])
        all = { "mesg" : mesg, "selectors" : selectors.getSelectorData(context), "username" : context.geek }
        return webserver.render("stats/selectionsDoc.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def viewCollection(request, param):
    import game_collections, features, selectors, generate, library
    features = [ features.GenericTable, features.PogoTable ]
    all = {}
    try:
        fields = param.split("/")
        if len(fields) == 3:
            context = interpretRequest(request, fields[0])
            index = int(fields[1])
            groupindex = int(fields[2])
        else:
            return webserver.render("stats/badurl.html", {}, request)
        collection = game_collections.getCollectionForGeek(context, index, True)
        groups = [ g for g in collection.groups if g.display ]
        group = collection.byGroup.get(groupindex)
        if group is None or not group.display:
            minIndex = min([g.index for g in groups ])
            return webserver.redirect("/dynamic/viewCollection/%s/%d/%d" % (context.geek, index, minIndex))
        selector = selectors.CollectionSelector(index, groupindex)
        groups.sort(lambda g1, g2: cmp(g1.index, g2.index))
        contents = []
        generate.addCollectionSummary(context, collection.groups)
        all = { "contents" : contents, "groups" : groups, "group" : group, "collection" : collection, "username" : context.geek,
                "visibleColumns" : "Name,Rating,Plays,Utilisation" }
        for f in features:
            ff = f(selector)
            all.update(ff.generate(context))
            contents.append(ff)
        return webserver.render("stats/viewCollection.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def editCollection(request, params):
    import selectors, library
    try:
        fields = params.split("/")
        if len(fields) == 2:
            context = interpretRequest(request, fields[0])
            index = int(fields[1])
            sels = selectors.getSelectorData(context)
            username = context.geek
            return webserver.render("stats/editCollection.html", locals(), request)
        else:
            return webserver.render("stats/badurl.html", {}, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def deleteCollection(request, params):
    import game_collections, library
    try:
        fields = params.split("/")
        if len(fields) == 2:
            context = interpretRequest(request, fields[0])
            index = int(fields[1])
            game_collections.deleteCollection(context, index)
            return webserver.redirect("/dynamic/collections/%s" % context.geek)
        else:
            return webserver.render("stats/badurl.html", {}, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def saveManageCollection(request):
    def post(key, singleton=False):
        v = request.POST.get(key)
        if v is not None and singleton and type(v) == type([]):
            v = v[0]
        return v
    import simplejson, library, game_collections
    try:
        geek = post("geek", True)
        username = library.checkGeek(geek, request)
        cindex = int(post("collection", True))
        model = post("model", True)
        model = simplejson.loads(model)
        game_collections.saveCollectionFromJson(username, cindex, model)
        data = { "success" : True }
        return webserver.response(simplejson.dumps(data), content_type="application/json")
    except library.NoSuchGeekException:
        data = { "success" : False, "message" : "User not found" }
        return webserver.response(simplejson.dumps(data), content_type="application/json")

def ajaxSubmit(request):
    import game_collections, simplejson
    results = { 'success' : False }
    form = game_collections.AjaxForm( request.GET )
    if form.is_valid():
        results['name'] = form.cleaned_data['input']
        results['success'] = True
    return webserver.response( simplejson.dumps( results ), mimetype='application/json' )

def listOfGeeks(request):
    import dbaccess
    names = dbaccess.getAllGeekNames()
    names.sort(lambda a,b: cmp(a.lower(), b.lower()))
    title = "Users of Extended Stats"
    return webserver.render("stats/list.html", { "title" : title, "items" : names }, request)

def ipod(request, param):
    import selectors, library
    try:
        context = interpretRequest(request, param)
        pbm = generate.getPBMData(context)
        favourites = generate.getFavourites(context, selectors.AllGamesSelector())
        favourites = favourites[:50]
        shouldPlayOwn = generate.getShouldPlayOwnData(context)
        (pogo, pogoCollections) = generate.getPogoData(context, selectors.OwnedGamesSelector())
        return webserver.render("stats/ipod_main.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/ipod_geek_error.html", locals(), request)

def selector(request, param):
    import library, simplejson
    result = []
    try:
        (context, selector) = interpretRequestAndSelector(request, param, "all")
        opts = library.Thing()
        opts.excludeExpansions = False
        opts.excludeTrades = False
        games = selector.getGames(context, opts)
        for g in games:
            d = { "name" : g.game.name, "id" : g.game.bggid }
            result.append(d)
    except library.NoSuchGeekException:
        pass
    return webserver.response(simplejson.dumps(result), content_type="application/json")

def collection(request, param):
    import simplejson, game_collections, library
    result = {}
    try:
        (context, params) = interpretRequestAndParams(request, param)
        cindex = int(params[0])
        try:
            c = context.substrate.getCollection(cindex)
        except KeyError:
            c = game_collections.makeNewCollection(context, cindex)
        result = { "name" : c.name, "description" : c.description, "index" : c.index }
        groups = []
        for g in c.groups:
            games = []
            for game in g.games:
                d = { "name" : game.name, "id" : game.bggid }
                games.append(d)
            gg = { "name" : g.name, "description" : g.description, "index" : g.index , "display" : g.display, "games" : games }
            groups.append(gg)
        result["groups"] = groups
    except library.NoSuchGeekException:
        pass
    return webserver.response(simplejson.dumps(result), content_type="application/json")

def whatif(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        games = generate.getWhatIfData(context)
        username = context.geek
        return webserver.render("stats/whatif.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def locations(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        locations = generate.getPlayLocationsData(context)
        username = context.geek
        return webserver.render("stats/locations_result.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def playscsv(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        plays = generate.getPlaysCSVData(context)
        username = context.geek
        return webserver.render("stats/plays.csv", locals(), request, mimetype="text/csv")
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def updates(request, param):
    import library, dbaccess
    try:
        context = interpretRequest(request, param)
        updates = dbaccess.getFilesForGeek(context.geek)
        updates.sort(lambda f1, f2: -cmp(f1.description, f2.description))
        return webserver.render("stats/updates.html", {"username" : context.geek, "updates" : updates}, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def refresh(request, param):
    import urllib2, mydb
    arg = request.META["REQUEST_URI"]
    if arg is not None and arg.startswith("/dynamic/refreshPage/"):
        param = arg[len("/dynamic/refreshPage/"):]
    if arg is None:
        errors = str(request.META)
    vals = {}
    vals.update(webserver.csrf(request))
    l = len(param)
    if param is None or len(param) > 190 or "'" in param:
        return webserver.render("stats/refresh.html", vals, request)
    param = urllib2.unquote(param)
    sql = "update files set lastUpdate = null where url = %s"
    result = mydb.update(sql, [param])
    return webserver.render("stats/refresh.html", vals, request)

def quickRefresh(request, param):
    if len(param) > 32 or "'" in param:
        return webserver.render("stats/refresh.html", locals(), request)
    import mydb
    sql = "update files set lastUpdate = null where geek = %s and char_length(tillNextUpdate) <= 8"
    with open("/tmp/url.txt", "w") as f:
        f.write(param + "\n" + str(request))
    mydb.update(sql, [param])
    return webserver.render("stats/refresh.html", locals(), request)

def numplayers(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        data = generate.getNumPlayersData(context)
        return webserver.render("stats/numplayers.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)


class Link(object):
    def __init__(self, url, name):
        self.url = url
        self.name = name

def playsLink(isTotals, *fields):
    s = "/".join(["", "dynamic", "plays"] + [str(f) for f in fields if f is not None])
    if isTotals:
        s += "/totals"
    return s

class CalendarMonth(object):
    def __init__(self, y, m, index):
        import calendar, library, datetime
        calendar.setfirstweekday(calendar.SUNDAY)
        self.year = y
        self.month = m
        self.name = "%04d-%02d" % (y, m)
        (startDay, daysInMonth) = calendar.monthrange(y, m)
        self.rows = []
        row = []
        if startDay < 6:
            row = [None] * (startDay+1)
        for date in range(daysInMonth):
            self.day = library.Thing()
            self.day.date = date+1
            self.day.dt = datetime.date(y, m, self.day.date)
            index[self.day.dt] = self.day
            row.append(self.day)
            if len(row) == 7:
                self.rows.append(row)
                row = []
        if len(row) > 0:
            self.rows.append(row)
        if len(self.rows) < 6:
            self.rows.append([library.Thing()])

def getCalendarMonths(startDate, endDate, index):
    y = startDate.year
    m = startDate.month
    result = []
    n = 0
    while (y * 12 + m <= endDate.year * 12 + endDate.month) and (n < 120):
        n += 1
        t = CalendarMonth(y, m, index)
        result.append(t)
        m += 1
        if m == 13:
            m = 1
            y += 1
    return result

def splitMonths(ms):
    result = []
    while len(ms) > 3:
        result.append(ms[:3])
        ms = ms[3:]
    result.append(ms)
    return result

def gamesCalendar(request, param):
    import datetime, intsequence, library
    try:
        fields = param.split("/")
        if len(fields) > 0:
            context = interpretRequest(request, fields[0])
            username = context.geek
            fields = fields[1:]
            opts = library.Thing()
            opts.excludeExpansions = False
            opts.excludeTrades = False
            (year, month, day, args, startDate, endDate) = library.getDateRangeForDescribedRange(fields)
            intSeq = intsequence.parseIntSequence(args)
            if endDate is None or endDate > datetime.date.today():
                endDate = datetime.date.today()
            index = {}
            months = getCalendarMonths(startDate, endDate, index)
            seq = intSeq.getCounts(context, opts, startDate, endDate)
            for (date, day) in index.items():
                day.count = seq[date]
                day.colour = library.playsToColour(day.count)
                day.tooltip = seq.getAnnotations(date)
                if day.tooltip is None:
                    day.tooltip = ""
                else:
                    day.tooltip = "\n".join(set(day.tooltip))
            months = splitMonths(months)
            return webserver.render("stats/calendars.html", locals(), request)
        else:
            return webserver.render("stats/badurl.html", {}, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def plays(request, param):
    import library
    try:
        fields = param.split("/")
        if len(fields) > 0:
            context = interpretRequest(request, fields[0])
            username = context.geek
            (plays, messages, year, month, day, args) = context.substrate.getPlaysForDescribedRange(fields[1:])
            links = []
            totals = "totals" in args
            florence = "florence" in args
            if not florence:
                if day is not None:
                    # month link
                    url = playsLink(totals, context.geek, year, month)
                    links.append(Link(url, "Plays for Month"))
                if month is not None:
                    # year link
                    url = playsLink(totals, context.geek, year)
                    links.append(Link(url, "Plays for Year"))
                    # all plays for user
                url = playsLink(totals, context.geek)
                links.append(Link(url, "All Plays for %s" % context.geek))
                if totals:
                    url = playsLink(False, context.geek, year, month, day)
                    links.append(Link(url, "Plays for this period"))
                else:
                    url = playsLink(True, context.geek, year, month, day)
                    links.append(Link(url, "Totals for this period"))
            if totals:
                plays = generate.totalPlays(plays)
                generate.addGeekData(context.geek, plays)
                return webserver.render("stats/totalplays.html", locals(), request)
            elif florence:
                data = generate.florenceData(plays)
                img = imggen.createFlorenceDiagram(context.geek, data)
                return library.imageResponse(img)
            generate.addGeekData(context.geek, plays)
            return webserver.render("stats/plays.html", locals(), request)
        else:
            return webserver.render("stats/badurl.html", {}, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def meta(request):
    items = [("%s = %s" % (k, v)) for (k,v) in request.META.items()]
    title = "Meta-Information Sent with the HTTP Request"
    return webserver.render("stats/list.html", locals(), request)

def checklist(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        rows = generate.getChecklistData(context)
        username = context.geek
        return webserver.render("stats/checklist.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def crazy(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        rows = generate.getCrazyRecommendationsData(context)
        username = context.geek
        return webserver.render("stats/crazy.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def getBrowser(request):
    return str(request.META.get("HTTP_USER_AGENT"))

def rankings(request, param):
    (categories, mechanics, title, data) = generate.getTopRankedData(param)
    return webserver.render("stats/rankings.html", locals(), request)

def playrate(request, param):
    import library
    try:
        (context, selector) = interpretRequestAndSelector(request, param, "all")
        import selectors, features
        data = generate.getPlayRateData(context, selector)
        (img, imap) = imggen.createPlayRateGraph(context, data)
        all =  {"username" : context.geek, "prdata" : features.imageBinaryData(img), "prmap": imap, "selector" : selector }
        return webserver.render("stats/playrate_result.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def normrankings(request, param):
    (categories, mechanics, title, data) = generate.getNormRankedData(param)
    return webserver.render("stats/normrankings.html", locals(), request)

def generic(request, param):
    import features, library
    try:
        (context, selector) = interpretRequestAndSelector(request, param, "all")
        feature = features.GenericTable(selector)
        all = feature.generate(context)
        visible = "Name,Rating,Plays"
        all.update({ "username" : context.geek, "visibleColumns" : visible, "title" : selector.name, "url" : "/dynamic/generic" })
        return webserver.render("stats/generic_result.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def gini(request, param):
    import features, library
    try:
        (context, selector) = interpretRequestAndSelectorChain(request, param, "played/owned")
        feature = features.GiniTable(selector)
        all = feature.generate(context)
        all.update({"username" : context.geek})
        return webserver.render("stats/gini_result.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def favourites(request, param):
    import features, library
    try:
        (context, selector) = interpretRequestAndSelector(request, param, "owned/rated/played/or/or")
        feature = features.Favourites(selector)
        all = feature.generate(context)
        visible = "Name,Rating,Plays,BGG Ranking,BGG Rating,First Played,Last Played,Months Played,Hours Played,FHM,HHM,R!UHM,Year Published"
        all.update({ "visibleColumns" : visible, "games" : all["favourites"], "username" : context.geek, "url" : "/dynamic/favourites" })
        return webserver.render("stats/favourites_result.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def favourites2(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        favourites = generate.getFavourites(context)
        bggCorrelation = generate.calcCorrelation(favourites)
        bggCorrelationRankedOnly = generate.calcCorrelationRankedOnly(favourites)
        hindex = generate.calcHIndex(favourites)
        return webserver.render("stats/favourites2_result.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def unusual(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        unusual = generate.getUnusualData(context)
        return webserver.render("stats/unusual_result.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def multiyear(request, param):
    import generate, library
    try:
        context = interpretRequest(request, param)
        (multiyear, myyears) = generate.getMultiYearData(context)
        return webserver.render("stats/multiyear_result.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def sgoyt(request, param):
    import generate
    geeklist = int(param)
    data = generate.sgoyt(param)
    return webserver.render("stats/sgoyt.html", locals(), request)

def playLogging(request, param):
    import generate, library
    try:
        context = interpretRequest(request, param)
        (players, locations) = generate.getPlayLoggingData(context)
        return webserver.render("stats/playlogging_result.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def server(request, param):
    return webserver.render("stats/server.html", locals(), request)

def recordProfileView(username):
    import mydb, datetime, library
    sql = "select profileViews from users where geek = %s"
    data = mydb.query(sql, [username])
    if len(data) == 0:
        sql = "INSERT INTO users (geek, profileViews) VALUES (%s, 0)"
        mydb.update(sql, [username])
        count = 0
    else:
        count = int(data[0][0])
    count += 1
    sql = "update users set lastProfileView = %s, profileViews = %s where geek = %s"
    now = library.dbTime(datetime.datetime.utcnow())
    mydb.update(sql, [now, count, username])

def comparativeYears(request, param):
    import generate, library
    try:
        context = interpretRequest(request, param)
        username = context.geek
        florence = imggen.getFlorenceSettings()
        playsYears = generate.getPlaysRecordedYears(context)
        return webserver.render("stats/yearcomparison.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def dimesByDesigner(request, param):
    import features, library
    try:
        context = interpretRequest(request, param)
        feature = features.DimesByDesigner()
        all = feature.generate(context)
        return webserver.render(feature.resultFile, all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def tabbed(request,  param):
    import generate, features, selectors, library
    try:
        all = {}
        tab = 1
        if "/" in param:
            tab = int(param[param.find("/")+1:])
            param = param[:param.find("/")]
        text = param
        MAXTABS = 7
        if tab < 1 or tab > MAXTABS:
            tab = 1
        context = interpretRequest(request, param)
        for t in range(1, MAXTABS+1):
            all["tab" + `t`] = (tab == t)
        if tab == 1:
            # General
            runFeatures([ features.Favourites(selectors.AllGamesSelector()),
                          features.OwnedByPublishedYear(context.options.upsideDownObpy),
                          features.RatingByPublishedYear(context.options.upsideDownRbpy), features.Florence(),
                          features.FavesByPublishedYear(), features.BestDays(),
                          features.RatingByRanking(), features.PlaysByRanking(), features.DimesByDesigner() ],
                        all, context)
            all['favourites'] = all['favourites'][:20]
            playsYears = generate.getPlaysRecordedYears(context)
            playsYearsRows = []
            PLAY_YEAR_WIDTH = 7
            while len(playsYears) > PLAY_YEAR_WIDTH:
                playsYearsRows.append(playsYears[:PLAY_YEAR_WIDTH])
                playsYears = playsYears[PLAY_YEAR_WIDTH:]
            if len(playsYears) > 0:
                playsYearsRows.append(playsYears)
            all['playsYearsRows'] = playsYearsRows
        elif tab == 2:
            # Plays
            runFeatures([
                features.PlayRate(selectors.makeSelector([], "played")), features.PlayRateOwn(),
                features.PlayRatePrevOwn(), features.PlaysByYear(), features.PlaysByMonthTimeline(),
                features.PlaysByMonthYTD(), features.PlaysByMonthEver(), features.PlaysByMonthGraph(),
                features.PlayRatings(), features.PlaysByQuarter(),
                features.TemporalHotnessMonth(), features.TemporalHotnessDate(), features.TemporalHotnessDay() ],
                all, context)
        elif tab == 3:
            # Collection Management
            ownedSelector = selectors.OwnedGamesSelector()
            runFeatures([
                features.PlaysByPublishedYear(context.options.upsideDownPbpy),
                features.Pogo(POGO_SELECTOR), features.PogoTable(POGO_SELECTOR),
                features.LeastWanted(), features.Unusual(), features.ShouldPlay(), features.ShouldPlayOwn() ],
                all, context)
        elif tab == 4:
            # What to Play
            runFeatures([ features.MostUnplayed() ], all, context)
        elif tab == 5:
            pass
        elif tab == 6:
            opts = context.options.user
            all.update(opts.__dict__)
            contents = []
            for feature in features.FEATURES:
                if feature.enabled(opts):
                    vs = feature.generate(context)
                    if vs is not None:
                        all.update(vs)
                        contents.append(feature)
            all["contents"] = contents
        elif tab == 7:
            runFeatures([features.FeatureList()], all, context)
        recordProfileView(context.geek)
        all.update({"username" : context.geek, "tab" : tab })
        return webserver.render("stats/result_tabbed.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def runFeatures(fs, all, context):
    firstpass = [(f, f.generate(context)) for f in fs]
    c = []
    for (f,d) in firstpass:
        if d is None:
            continue
        # t looks like the feature but it's serializable for JSON
        t = { "cssClass" : f.cssClass, "htmlFile" : f.htmlFile, "tag" : f.tag, "title" : f.title }
        if f.contentsFile is not None:
            t["contentsFile"] = f.contentsFile
        c.append(t)
        all.update(d)
    all['contents'] = c

def featureList(request, param):
    import features, library
    try:
        context = interpretRequest(request, param)
        all = {}
        all.update({"username" : context.geek })
        runFeatures([features.FeatureList()], all, context)
        return webserver.render("stats/featurelist_result.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def result(request, param):
    import features, selectors, library
    try:
        context = interpretRequest(request, param)
        all = {}
        ownedSelector = selectors.OwnedGamesSelector()
        allSelector = selectors.AllGamesSelector()
        fs = [ features.Favourites(allSelector), features.PlaysByPublishedYear(False), features.OwnedByPublishedYear(False),
               features.RatingByPublishedYear(False), features.Florence(), features.Morgan(),
               features.Pogo(POGO_SELECTOR), features.PogoTable(POGO_SELECTOR),
               features.MostUnplayed(), features.PlayRate(selectors.makeSelector([], "played")), features.PlayRateOwn(), features.PlaysByMonthTimeline(),
               features.PlaysByMonthEver(), features.PlaysByMonthYTD(), features.PlaysByMonthGraph(),
               features.FavesByPublishedYear(), features.BestDays(), features.RatingByRanking(), features.PlayRatings(),
               features.LeastWanted(), features.Unusual(), features.ShouldPlay(), features.ShouldPlayOwn(), features.YearlySummaries(),
               features.DimesByDesigner() ]
        runFeatures(fs, all, context)
        all['favourites'] = all['favourites'][:20]
        all['username'] = context.geek
        all.update(locals())
        all["selectors"] = selectors.getSelectorData(context)
        recordProfileView(context.geek)
        return webserver.render("stats/result.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def consistency(request, param):
    import selectors, features, library
    try:
        fields = param.split("/")
        if len(fields) > 1:
            context = interpretRequest(request, fields[0])
            months = int(fields[1])
            if len(fields) > 2:
                selector = selectors.getSelectorFromFields(fields[2:])
            else:
                selector = selectors.getSelectorFromFields(["played"])
        else:
            return webserver.render("stats/badurl.html", {}, request)
        if months <= 0:
            months = 96
        f = features.Consistency(selector, months)
        all = { "username" : context.geek }
        runFeatures([f], all, context)
        return webserver.render("stats/consistency_result.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def choose(request, param):
    import features, library
    try:
        fields = param.split("/")
        if len(fields) == 0:
            fields = ["Friendless"]
        context = interpretRequest(request, fields[0])
        featuresByKey = features.FEATURES_BY_KEY
        keys = []
        contents = []
        for f in fields[1:]:
            ffs = f.split("&")
            for ff in ffs:
                if featuresByKey.get(ff) and ff not in keys:
                    keys.append(ff)
                    contents.append(featuresByKey[ff])
        all = { "username" : context.geek }
        runFeatures(contents, all, context)
        return webserver.render("stats/choose.html", all, request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def json(request, param):
    import features, simplejson, library
    try:
        fields = param.split("/")
        if len(fields) == 0:
            fields = ["Friendless"]
        context = interpretRequest(request, fields[0])
        featuresByKey = features.FEATURES_BY_KEY
        keys = []
        contents = []
        for f in fields[1:]:
            ffs = f.split("&")
            for ff in ffs:
                if featuresByKey.get(ff) and ff not in keys:
                    keys.append(ff)
                    contents.append(featuresByKey[ff])
        all = { "username" : context.geek }
        runFeatures(contents, all, context)
        all["success"] = True
        j = simplejson.dumps(all, default=library.jsonEncode)
        return webserver.response(j, content_type="application/json")
    except library.NoSuchGeekException:
        data = { "success" : False, "message" : "User not found" }
        return webserver.response(simplejson.dumps(data), content_type="application/json")

def year(request, param):
    import library
    try:
        fields = param.split("/")
        if len(fields) > 0:
            context = interpretRequest(request, fields[0])
            year = int(fields[1])
        else:
            return webserver.render("stats/badurl.html", {}, request)
        username = context.geek
        florence = imggen.getFlorenceSettings()
        florenceDefault = str(year)
        morePieDefault = str(year)
        playsYears = generate.getPlaysRecordedYears(context)
        bestDays = generate.getBestDays(context, year)[:20]
        designerDimes = generate.getDimesByDesigner(context, year)
        ndd = generate.getNickelAndDime(context, year)
        playedLastYear = generate.getPlayedLastYearNotThis(context, year)
        return webserver.render("stats/year.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def frontPage(request):
    playsData = generate.getFrontPagePlaysData()
    return webserver.render("stats/front_page.html", locals(), request)

def australiaFrontPage(request):
    playsData = generate.getAustraliaFrontPagePlaysData()
    return webserver.render("stats/front_page.html", locals(), request)

def splitIntoRows(objects, n):
    result = []
    while len(objects) > 0:
        result.append(objects[:n])
        objects = objects[n:]
    return result

def categoryGraphs(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        catsToGraph = splitIntoRows(generate.getCategoriesToGraph(context), 4)
        mecsToGraph = splitIntoRows(generate.getMechanicsToGraph(context), 4)
        dessToGraph = splitIntoRows(generate.getDesignersToGraph(context), 4)
        pubsToGraph = splitIntoRows(generate.getPublishersToGraph(context), 4)
        return webserver.render("stats/catgraphs.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def series(request, param):
    import library
    try:
        context = interpretRequest(request, param)
        series = generate.getSeriesData(context)
        username = context.geek
        return webserver.render("stats/series.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

GRAPH_METHODS = { "category" : generate.getCategoriesToGraph,
                  "mechanic" : generate.getMechanicsToGraph,
                  "designer" : generate.getDesignersToGraph,
                  "publisher" : generate.getPublishersToGraph }

def category(request, param):
    import library
    try:
        fields = param.split("/")
        if len(fields) > 0:
            context = interpretRequest(request, fields[0])
            username = context.geek
            typ = fields[1]
            if typ not in GRAPH_METHODS.keys():
                return webserver.render("stats/badurl.html", {}, request)
        else:
            return webserver.render("stats/badurl.html", {}, request)
        rows = generate.getCatMecData(context, typ)
        toGraph = splitIntoRows(GRAPH_METHODS[typ](context), 4)
        return webserver.render("stats/cat_%s.html" % typ, locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)

def trade(request, param):
    import library
    try:
        fields = param.split("/")
        if len(fields) != 1:
            return webserver.render("stats/badurl.html", {}, request)
        context = interpretRequest(request, fields[0])
        username = context.geek
        (country, geeks, games, mostWanted, leastWanted) = generate.getTradeData(context)
        username = context.geek
        return webserver.render("stats/trade.html", locals(), request)
    except library.NoSuchGeekException:
        return webserver.render("stats/geek_error.html", locals(), request)
