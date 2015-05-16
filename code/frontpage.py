import math
LAMBDA = math.log(0.1) / -10.0

def updateFrontPageData(geek):
    import time
    start = time.time()
    fpg = FrontPageGeek(geek)
    getFrontPagePlaysData(fpg)
    fpg.save()
    end = time.time()
    diff = int((end - start) * 1000)
    return fpg

def uses(g1, g2):
    c = -cmp(g1, g2)
    return c

class FrontPageGeek(object):
    def __init__(self, geek):
        self.geek = geek
        self.totalPlays = 0
        self.distinctGames = 0
        self.top50 = 0
        self.sdj = 0
        self.the100 = 0
        self.owned = 0
        self.want = 0
        self.wish = 0
        self.trade = 0
        self.prevOwned = 0  
        self.friendless = 0
        self.utilisation = 0.0
        self.cfm = 0.0
        self.tens = 0
        self.zeros = 0
        self.ext100 = 0
        self.mv = 0
        
    def normalise(self):
        self.cfm = int(self.cfm * 10.0) / 10.0
        self.utilisation = int(self.utilisation * 10.0) / 10.0
        
    def toMap(self):
        result = {}
        for key in ["geek", "totalPlays", "distinctGames", "top50", "sdj", "the100", "owned", "want", "wish", "trade",
                    "prevOwned", "friendless", "utilisation", "cfm", "tens", "zeros", "ext100", "mv"]:
            result[key] = self.__dict__[key]
        return result
        
    def save(self):
        import mydb
        mydb.saveRow(self.toMap(), "frontpagegeek", "geek = '%s'" % self.geek, False)
        
def getFrontPagePlaysData(fpg):
    import mydb
    sql = "select sum(quantity), count(distinct game) from plays where game not in (select gameId from gameCategories where category = 'Book') and geek = %s"
    data = mydb.query(sql, [fpg.geek])
    playsData = []
    for (q, d) in data:
        if q is None:
            q = 0
        if d is None:
            d = 0
        fpg.totalPlays = q
        fpg.distinctGames = d
    sql = "select sum(owned), sum(want), sum(wish>0), sum(trade), sum(prevowned) from geekgames where geek = %s"
    data = mydb.query(sql, [fpg.geek])
    for (owned, want, wish, trade, prevowned) in data:
        if owned is None:
            owned = 0
        if want is None:
            want = 0
        if wish is None:
            wish = 0
        if trade is None:
            trade = 0
        if prevowned is None:
            prevowned = 0
        fpg.owned = owned
        fpg.want = want
        fpg.wish = wish
        fpg.trade = trade
        fpg.prevOwned = prevowned
    sql = 'select name, count(distinct game) from (select t2.name, t2.game, plays.geek from plays, (select name, game from series where name in ("Top 50", "The 100", "Spiel des Jahre", "Extended Stats Top 100", "Most Voters")) t2 where plays.game = t2.game and plays.geek = %s) t1 group by name'
    data = mydb.query(sql, [fpg.geek])
    for (series, count) in data:
        if series == "Spiel des Jahre":
            fpg.sdj = count
        elif series == "Top 50":
            fpg.top50 = count
        elif series == "The 100":
            fpg.the100 = count
        elif series == "Extended Stats Top 100":
            fpg.ext100 = count
        elif series == "Most Voters":
            fpg.mv = count
    getFrontPageFriendlessMetricData(fpg)    

def calcFriendless(data):
    import library
    data.sort(uses)
    ld = len(data)
    tens = 0
    zeros = 0
    for p in data:
        if p >= 10:
            tens = tens + 1
        elif p == 0:
            zeros = zeros + 1
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
    return (friendless, utilisation, cfm, tens, zeros)
    
def getFrontPageFriendlessMetricData(fpg):
    import mydb
    sql = "select game, sum(quantity) from geekgames left outer join plays using (geek, game) where owned = True and game not in (select gameId from gameCategories where category = 'Book') and geek = %s group by game"
    data = mydb.query(sql, [fpg.geek])
    fpg.games = []
    for (id, q) in data:
        if q is None:
            q = 0
        fpg.games.append(q)   
    (friendless, utilisation, cfm, tens, zeros) = calcFriendless(fpg.games)     
    fpg.friendless = friendless
    fpg.utilisation = utilisation
    fpg.cfm = cfm
    fpg.tens = tens
    fpg.zeros = zeros       
