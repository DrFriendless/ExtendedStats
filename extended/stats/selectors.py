class Stack(object):
    def __init__(self):
        self.data = []
        self.columns = None
        
    def append(self, thing):
        self.data.append(thing)
        
    def pop(self):
        return self.data.pop()
        
    def __getitem__(self, index):
        return self.data[index]
        
    def __len__(self):
        return len(self.data)

def makeSelector(fields, default):
    if len(fields) == 0:
        if type(default) == type([]):
            fields = default
        else:
            fields = [ default ]
    key = fields[0]
    args = fields[1:]
    c = CLASS_BY_KEY[key]
    return apply(c, args[:c.arity])
    
class UnknownSymbol(Exception):
    def __init__(self, symbol):
        self.symbol = symbol
        
    def __str__(self):
        return "Unknown symbol: %s" % self.symbol
    
class IncorrectArgs(Exception):
    def __init__(self, symbol, arity):
        self.symbol = symbol
        self.arity = arity
        
    def __str__(self):
        return "Incorrect arguments: %s takes %d args" % (self.symbol, self.arity)
    
def parseSelectorChain(fields):
    chain = []
    while len(fields) > 0:
        key = fields[0]
        if key.startswith('"'):
            if key.startswith('"'):
                key = key[1:]
            if key.endswith('"'):
                key = key[:-1]
            chain.append(NameOperator(key))
            fields = fields[1:]
        elif CLASS_BY_KEY.get(key) is not None:
            # a selector
            c = CLASS_BY_KEY[key]
            fields = fields[1:]
            args = fields[:c.arity]
            fields = fields[c.arity:]
            if len(args) != c.arity:
                raise IncorrectArgs(key, c.arity)
            chain.append(apply(c, args))
        elif OP_BY_KEY.get(key) is not None:
            # an operator
            c = OP_BY_KEY[key]
            fields = fields[1:]
            args = fields[:c.arity]
            fields = fields[c.arity:]
            chain.append(apply(c, args))
        else:
            raise UnknownSymbol(fields[0])
    return chain
    
def interpretChain(chain):
    stack = Stack()
    for element in chain:
        if isinstance(element, Selector):
            stack.append(element)
        else:
            element.operate(stack)
    return stack
    
def getSelectorFromString(s):
    fields = s.split("/")
    if fields[0] == "":
        fields = fields[1:]
    return getSelectorFromFields(fields)    
    
def getSelectorsFromString(s):
    fields = s.split("/")
    if fields[0] == "":
        fields = fields[1:]
    return getSelectorsFromFields(fields)

def getSelectorFromFields(fields):
    chain = parseSelectorChain(fields)
    stack = interpretChain(chain)
    return stack[-1]
    
def getSelectorsFromFields(fields):
    try:
        chain = parseSelectorChain(fields)
        stack = interpretChain(chain)
        return stack
    except UnknownSymbol, s:
        import views
        raise views.BadUrlException(s)
    
def getSelectorData(context):    
    import library
    result = []
    for s in SIMPLE_SELECTORS:
        t = library.Thing()
        t.name = s.name
        t.fragment = s.fragment
        result.append(t)
    opts = library.Thing()
    opts.excludeExpansions = False
    opts.excludeTrades = False
    cats = context.substrate.getAllCategories(opts)
    cats.sort()
    for c in cats:
        s = CategorySelector(c)
        t = library.Thing()
        t.name = s.name
        t.fragment = s.fragment
        result.append(t)        
    cats = context.substrate.getAllMechanics(opts)
    cats.sort()
    for c in cats:
        s = MechanicSelector(c)
        t = library.Thing()
        t.name = s.name
        t.fragment = s.fragment
        result.append(t)        
    series = context.substrate.getAllSeries()
    series = series.keys()[:]
    series.sort()
    for c in series:
        s = SeriesSelector(c)
        t = library.Thing()
        t.name = s.name
        t.fragment = s.fragment
        result.append(t)        
    cats = context.substrate.getAllDesigners(opts)
    cats.sort()
    for c in cats:
        s = DesignerSelector(c)
        t = library.Thing()
        t.name = s.name
        t.fragment = s.fragment
        result.append(t)        
    return result
    
class Selector(object):
    def __init__(self, name, fragment):
        self.name = name
        self.fragment = fragment
        
    def getGames(self, context, opts):
        return []
        
class SeriesSelector(Selector):
    key = "series"
    arity = 1
    def __init__(self, name):
        Selector.__init__(self, name, SeriesSelector.key + "/" + name)
        
    def getGames(self, context, opts):
        allSeries = context.substrate.getAllSeries()
        return context.substrate.getTheseGeekGames(allSeries[self.name])

class GameSelector(Selector):
    key = "game"
    arity = 1
    def __init__(self, n):
        Selector.__init__(self, None, GameSelector.key + "/" + n)
        self.n = int(n)
        self.name = "Game " + `self.n`
        
    def getGames(self, context, opts):
        g = context.substrate.getGames([self.n]).get(self.n)
        if g is None:
            # no such game - you can have E&T instead!
            gs = context.substrate.getGames([42])
        else:
            gs = context.substrate.getGames([self.n])
        return context.substrate.getTheseGeekGames(gs.values())

class AllGamesSelector(Selector):
    key = "all"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "All Games", AllGamesSelector.key)
    
    def getGames(self, context, opts):
        return context.substrate.getAllGeekGamesWithOptions(opts)
        
class OwnedGamesSelector(Selector):
    key = "owned"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Owned Games", OwnedGamesSelector.key)
    
    def getGames(self, context, opts):  
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)
        return [ gg for gg in allGames if gg.owned ]
        
class PreviouslyOwnedGamesSelector(Selector):
    key = "prevowned"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Previously Owned Games", PreviouslyOwnedGamesSelector.key)
    
    def getGames(self, context, opts):  
        return context.substrate.getPreviouslyOwnedGames(opts)
        
class RatedGamesSelector(Selector):
    key = "rated"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Rated Games", RatedGamesSelector.key)
    
    def getGames(self, context, opts):  
        return context.substrate.getAllRatedGames(opts)      
        
class RatingSelector(Selector):
    key = "rating"
    arity = 2
    def __init__(self, op, value):
        self.predicate = makePredicate(op, value)
        Selector.__init__(self, "Rating " + `self.predicate`, RatingSelector.key)
    
    def getGames(self, context, opts):  
        all = context.substrate.getAllRatedGames(opts)      
        return [ gg for gg in all if self.predicate.matches(gg.rating) ]
        
def makePredicate(op, value):
    n = int(value)
    if op == "lt":
        return LessThanPredicate(n)
    elif op == "gt":
        return GreaterThanPredicate(n)
    elif op == "eq":
        return EqualsPredicate(n)
    elif op == "le":
        return LessThanEqualsPredicate(n)
    elif op == "ge":
        return GreaterThanEqualsPredicate(n)
    else:
        import views
        raise views.BadUrlException("Predicate operator %s not understood" % op)
        
class LessThanPredicate(object):
    def __init__(self, n):
        self.n = n
    
    def matches(self, v):
        return  v < self.n   
        
class GreaterThanPredicate(object):
    def __init__(self, n):
        self.n = n
    
    def matches(self, v):
        return  v > self.n   
        
class LessThanEqualsPredicate(object):
    def __init__(self, n):
        self.n = n
    
    def matches(self, v):
        return  v <= self.n   
        
class GreaterThanEqualsPredicate(object):
    def __init__(self, n):
        self.n = n
    
    def matches(self, v):
        return  v >= self.n   
        
class EqualsPredicate(object):
    def __init__(self, n):
        self.n = n
    
    def matches(self, v):
        return  v == self.n   
        
class WishlistSelector(Selector):
    key = "wishlist"
    arity = 1
    def __init__(self, values):
        Selector.__init__(self, "Wishlist", WishlistSelector.key + "/" + values)
        self.values = [ int(c) for c in values ]
    
    def getGames(self, context, opts):  
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)  
        return [ gg for gg in allGames if int(gg.wish) in self.values ]
        
class WantSelector(Selector):
    key = "want"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Want", WantSelector.key)
    
    def getGames(self, context, opts):  
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)  
        return [ gg for gg in allGames if gg.want ]
        
class TradeSelector(Selector):
    key = "trade"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Trade", TradeSelector.key)
    
    def getGames(self, context, opts):  
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)  
        return [ gg for gg in allGames if gg.trade ]
        
class WantToBuySelector(Selector):
    key = "wanttobuy"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Want to Buy", WantToBuySelector.key)
    
    def getGames(self, context, opts):  
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)  
        return [ gg for gg in allGames if gg.wanttobuy ]
        
class WantToPlaySelector(Selector):
    key = "wanttoplay"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Want to play", WantToPlaySelector.key)
    
    def getGames(self, context, opts):  
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)  
        return [ gg for gg in allGames if gg.wanttoplay ]
        
class PreorderedSelector(Selector):
    key = "preordered"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Preordered", PreorderedSelector.key)
    
    def getGames(self, context, opts):  
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)  
        return [ gg for gg in allGames if gg.preordered ]
        
class PlayedGamesSelector(Selector):
    key = "played"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Played Games", PlayedGamesSelector.key)
    
    def getGames(self, context, opts):  
        return context.substrate.getAllPlayedGames(opts)    
        
class CategorySelector(Selector):  
    key = "category"
    arity = 1
    def __init__(self, name):    
        import library
        name = library.esc(name)
        Selector.__init__(self, "Category %s" % name, CategorySelector.key + "/%s"  % name)
        self.cat = name
        self.name = name
        
    def getGames(self, context, opts):
        import mydb, substrate
        sql = "select gameId from gameCategories where category = %s"
        data = mydb.query(sql, [self.cat])
        data = [ d[0] for d in  data ]
        return context.substrate.getTheseGeekGames(substrate.getGames(data).values())
        
class BookSelector(CategorySelector):
    key = "books"
    arity = 0
    def __init__(self):
        CategorySelector.__init__(self, "Book")    
        
class MechanicSelector(Selector):  
    key = "mechanic"
    arity = 1
    def __init__(self, name):    
        import library
        name = library.esc(name)
        Selector.__init__(self, "Mechanic %s" % name, MechanicSelector.key + "/%s"  % name)
        self.cat = name
        self.name = name
        
    def getGames(self, context, opts):
        import mydb, substrate
        sql = "select gameId from gameMechanics where mechanic = %s"
        data = mydb.query(sql, [self.cat])
        data = [ d[0] for d in  data ]
        return context.substrate.getTheseGeekGames(substrate.getGames(data).values())
        
class ExpansionSelector(Selector):  
    key = "expansion"
    arity = 0
    def __init__(self):
        Selector.__init__(self, "Expansions", ExpansionSelector.key)
        
    def getGames(self, context, opts):
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)
        return [ gg for gg in allGames if gg.game.expansion ]
        
GEEKLIST_URL = "http://boardgamegeek.com/xmlapi/geeklist/%d?comments=0"
        
class GeeklistSelector(Selector):  
    key = "geeklist"
    arity = 1
    def __init__(self, id):
        Selector.__init__(self, "Geeklist", GeeklistSelector.key)  
        self.id = int(id)      
        
    def getGames(self, context, opts):
        import sitedata, views, xml.dom.minidom, substrate, library
        dest = sitedata.dbdir + "geeklist_%d_%s.xml" % (self.id, context.geek)
        url = GEEKLIST_URL % self.id
        success = library.getFile(url, dest)
        if not success:
            raise views.BadUrlException("Failed to download geeklist XML from %s" % url)
        result = []
        try:
            dom = xml.dom.minidom.parse(dest)      
            geeklist = dom.getElementsByTagName("geeklist")[0]
            gameNodes = geeklist.getElementsByTagName("item")            
            for gameNode in gameNodes:
                try:
                    g = int(gameNode.getAttribute("objectid"))
                    result.append(g)
                except AttributeError:
                    continue            
            games = substrate.getGames(result)
            return context.substrate.getTheseGeekGames(games.values())
        except xml.parsers.expat.ExpatError, e:
            raise views.BadUrlException("Error retrieving parsing geeklist: %s" % url)
        
class PlayedInYearSelector(Selector):  
    key = "piy"
    arity = 1
    def __init__(self, year):
        self.year = int(year)
        if self.year == 0:
            import library
            self.year = library.TODAY.year
        Selector.__init__(self, "Played in %d" % self.year, PlayedInYearSelector.key)
        
    def getGames(self, context, opts):
        import datetime
        games = []
        plays = context.substrate.filterPlays(datetime.date(self.year, 1, 1), datetime.date(self.year, 12, 31))[0]
        for p in plays:
            if p.game is not None and p.game.bggid not in games:
                games.append(p.game.bggid)
            for e in p.expansions:
                if e is not None and e.bggid not in games:
                   games.append(e.bggid)
        return context.substrate.getGeekGames(games)
        
class FirstPlayedInYearSelector(Selector):  
    key = "fpiy"
    arity = 1
    def __init__(self, year):
        self.year = int(year)
        if self.year == 0:
            import library
            self.year = library.TODAY.year
        Selector.__init__(self, "First Played in %d" % self.year, FirstPlayedInYearSelector.key)
        
    def getGames(self, context, opts):
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)
        return [ gg for gg in allGames if gg.firstPlay is not None and gg.firstPlay.year == self.year ]
        
class LastPlayedInYearSelector(Selector):  
    key = "lpiy"
    arity = 1
    def __init__(self, year):
        self.year = int(year)
        if self.year == 0:
            import library
            self.year = library.TODAY.year
        Selector.__init__(self, "Last Played in %d" % self.year, FirstPlayedInYearSelector.key)
        
    def getGames(self, context, opts):
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)
        return [ gg for gg in allGames if gg.lastPlay is not None and gg.lastPlay.year == self.year ]
        
class PlayedInMonthSelector(Selector):  
    key = "pim"
    arity = 2
    def __init__(self, year, month):
        self.year = int(year)
        self.month = int(month)        
        Selector.__init__(self, "Played in %d/%d" % (self.year, self.month), PlayedInMonthSelector.key)
        
    def getGames(self, context, opts):
        import datetime, calendar
        games = []
        daysInMonth = calendar.monthrange(self.year, self.month)[1]      
        plays = context.substrate.filterPlays(datetime.date(self.year, self.month, 1), datetime.date(self.year, self.month, daysInMonth))[0]
        for p in plays:
            if p.game is not None and p.game.bggid not in games:
                games.append(p.game.bggid)
            for e in p.expansions:
                if e is not None and e.bggid not in games:
                   games.append(e.bggid)
        return context.substrate.getGeekGames(games)
        
class DesignerSelector(Selector):  
    key = "designer"
    arity = 1
    def __init__(self, designer):    
        if type(designer) == type([]):
            designer = designer[0]
        if type(designer) == type("") or type(designer) == type(u""):
            designer = int(designer)
        if type(designer) == type(0):
            # create a fake designer
            import library, mydb
            self.designer = library.Thing()
            self.designer.bggid = designer
            self.name = mydb.query("select name from designers where bggid = " + `designer`)[0][0]
        else:
            Selector.__init__(self, "Designer %s" % designer.name, DesignerSelector.key + "/%d"  % designer.bggid)
            self.designer = designer
            self.name = designer.name
        
    def getGames(self, context, opts):
        import mydb
        gids = mydb.query("select gameId from gameDesigners where designerId = " + `self.designer.bggid`)
        gids = [ gid[0] for gid in gids ]
        games = context.substrate.getGames(gids)
        return context.substrate.getTheseGeekGames(games.values())
        
class CollectionSelector(Selector):
    key = "collection"
    arity = 2
    def __init__(self, collectionIndex, groupIndex):
        Selector.__init__(self, "Collection/%d/%d" % (collectionIndex, groupIndex), CollectionSelector.key + "/%d/%d"  % (collectionIndex, groupIndex))
        self.collectionIndex = collectionIndex
        self.groupIndex = groupIndex
        
    def getGames(self, context, opts):  
        allGames = context.substrate.getAllGeekGamesWithOptions(opts)
        collection = context.substrate.getCollection(self.collectionIndex)
        group = collection.byGroup[self.groupIndex]
        self.name = group.name
        gids = [ g.bggid for g in group.games ]
        result = [ gg for gg in allGames if gg.game.bggid in gids ]
        return result
        
class ThisSelector(Selector):
    def __init__(self, games):
        self.games = games
        self.name = "This"
    
    def getGames(self, context, opts):
        return self.games
        
class AndSelector(Selector):
    def __init__(self, left, right):
        self.name = "And"
        self.left = left
        self.right = right
    
    def getGames(self, context, opts):
        l = self.left.getGames(context, opts)
        r = self.right.getGames(context, opts)
        return inter(l, r)
        
class OrSelector(Selector):
    def __init__(self, left, right):
        self.name = "Or"
        self.left = left
        self.right = right
    
    def getGames(self, context, opts):
        l = self.left.getGames(context, opts)
        r = self.right.getGames(context, opts)
        return union(l, r)
        
class MinusSelector(Selector):
    def __init__(self, left, right):
        self.name = "Minus"
        self.left = left
        self.right = right
    
    def getGames(self, context, opts):
        l = self.left.getGames(context, opts)
        r = self.right.getGames(context, opts)
        return minus(l, r)
        
class GeekSelector(Selector):
     def __init__(self, geek, selector):
         self.geek = geek
         self.selector = selector
     
     def getGames(self, context, opts):
         ctx = context.getGeekContext(self.geek)
         ctxGeekGames = self.selector.getGames(ctx, opts)    
         ctxGames = [ gg.game for gg in ctxGeekGames ]
         return context.substrate.getTheseGeekGames(ctxGames)
        
SELECTOR_CLASSES = [ AllGamesSelector, OwnedGamesSelector, PreviouslyOwnedGamesSelector, RatedGamesSelector, PlayedGamesSelector, 
                    CategorySelector, MechanicSelector, DesignerSelector, CollectionSelector, WishlistSelector, WantSelector, TradeSelector,
                    WantToBuySelector, WantToPlaySelector, PreorderedSelector, ExpansionSelector, PlayedInYearSelector,
                    PlayedInMonthSelector, FirstPlayedInYearSelector, LastPlayedInYearSelector, SeriesSelector, RatingSelector,
                    BookSelector, GeeklistSelector, GameSelector ]
SIMPLE_SELECTORS = [ AllGamesSelector(), OwnedGamesSelector(), PreviouslyOwnedGamesSelector(), RatedGamesSelector(), PlayedGamesSelector(),
                    WishlistSelector("1234"), WantSelector(), TradeSelector(), WantToBuySelector(), WantToPlaySelector(), PreorderedSelector(),
                    ExpansionSelector(), BookSelector() ]
CLASS_BY_KEY = {}
for c in SELECTOR_CLASSES:
    CLASS_BY_KEY[c.key] = c
    
def contains(games, game):
    return game.bggid in [ g.bggid for g in games ]    
    
def union(games1, games2):
    ids = [ g.bggid for g in games1 ] 
    return games1 + [ g for g in games2 if g.bggid not in ids ]
    
def inter(games1, games2):
    ids = [ g.bggid for g in games1 ] 
    return [ g for g in games2 if g.bggid in ids ]
    
def minus(games1, games2):
    ids = [ g.bggid for g in games2 ] 
    return [ g for g in games1 if g.bggid not in ids ]
    
class Operator(object):
    def __init__(self):
        pass
        
class UnionOperator(Operator):
    arity = 0
    key = "or"
    
    def operate(self, stack):
        right = stack.pop()
        left = stack.pop()
        stack.append(OrSelector(left, right))
    
class DupOperator(Operator):
    arity = 1
    key = "dup"
    
    def __init__(self, offset):
        self.offset = int(offset) 
    
    def operate(self, stack):
        arg = stack[-(1+self.offset)]
        stack.append(arg)
    
class IntersectionOperator(Operator):
    arity = 0
    key = "and"

    def operate(self, stack):
        right = stack.pop()
        left = stack.pop()
        stack.append(AndSelector(left, right))
    
class MinusOperator(Operator):
    arity = 0
    key = "minus"
    
    def operate(self, stack):
        right = stack.pop()
        left = stack.pop()
        stack.append(MinusSelector(left, right))
        
class MapOperator(Operator):
    arity = 1
    key = "map"
    
    def __init__(self, op):
        self.op = OP_BY_KEY[op]()   
    
    def operate(self, stack):
        right = stack.pop()
        self.applyToAll(stack, right)
        
    def applyToAll(self, stack, right):
        if len(stack) == 0:
            return
        left = stack.pop()
        self.applyToAll(stack, right)
        name = left.name
        # apply the operation to our saved value and put it back
        stack.append(left)
        stack.append(right)
        self.op.operate(stack)
        # copy the name into the top of the stack
        left = stack.pop()
        left.name = name
        stack.append(left)
        
class GeekOperator(Operator):
    arity = 1    
    key = "geek"
    
    def __init__(self, name):
        import library
        self.name = library.esc(name) 
        
    def operate(self, stack):
        left = stack.pop()
        stack.append(GeekSelector(self.name, left))        
        
class NameOperator(Operator):
    arity = 0
    def __init__(self, name):
        self.name = name        
        
    def operate(self, stack):
        left = stack.pop()
        left.name = self.name
        stack.append(left)
        
class ColumnsOperator(Operator):
    arity = 1
    key = "columns"

    def __init__(self, columns):
        import library
        self.columns = [ library.esc(s.strip()) for s in columns.split(",") ]
        
    def operate(self, stack):
        stack.columns = self.columns
        
OPERATOR_CLASSES = [ UnionOperator, IntersectionOperator, MinusOperator, DupOperator, MapOperator, GeekOperator, ColumnsOperator ]
OP_BY_KEY = {}
for c in OPERATOR_CLASSES:
    OP_BY_KEY[c.key] = c
