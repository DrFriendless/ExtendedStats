def makeTooltip(games):
    if len(games) == 0:
        return ""
    names = [g.name for g in games]
    return ", ".join(names)

class Period:
    def __init__(self, name, opts):
        self.name = name
        self.opts = opts
        self.playsByGame = {}

    def addPlaysForGame(self, game, count):
        before = self.playsByGame.get(game)
        if before is None:
            before = 0
        after = before + count
        result = []
        if before < 5 <= after:
            result.append(5)
        if before < 10 <= after:
            result.append(10)
        if before < 25 <= after:
            result.append(25)
        if before < 100 <= after:
            result.append(100)
        self.playsByGame[game] = after
        return result

    def calcHIndex(self):
        plays = self.playsByGame.values()[:]
        plays.sort(lambda n1,  n2: cmp(n2,  n1))
        h = 0
        while len(plays) > h and plays[h] > h:
            h += 1
        return h

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def calculatePercentPlayed(self, gamesOwned):
        if len(gamesOwned) == 0:
            return 0.0
        count = len([g for g in self.playsByGame.keys() if g in gamesOwned])
        return count * 100.0 / len(gamesOwned)

    def toMap(self):
        pbg = { g.bggid : d for (g,d) in self.playsByGame.items() }
        return { "name" : self.name, "playsByGame" : pbg }

class Month(Period):
    def __init__(self, name, opts):
        Period.__init__(self, name, opts)
        self.year = int(self.name[:4])
        self.month = int(self.name[5:])
        self.plays = []
        self.count = 0
        self.played = set()
        self.expPlayed = set()
        self.new = set()
        self.newExpPlayed = set()
        self.nickels = set()
        self.dimes = set()
        self.hotGames = set()
        self.everNickels = set()
        self.everDimes = set()
        self.everQuarters = set()
        self.everDollars = set()
        self.january = (self.month == 1)
        self.daysPlayedOn = set()

    def calcHotGames(self, playsSoFar, ratingsForGames):
        scores = {}
        for (game, count) in self.playsByGame.items():
            rating = ratingsForGames.get(game)
            if rating is None or rating < 1:
                rating = 5.0
            scores[game] = count * game.playtime * rating / 300.0
            if playsSoFar.get(game) is not None:
                psf = playsSoFar[game]
                if psf + count > 0:
                    scores[game] += (count / (psf + count)) * 10
        if len(scores) > 0:
            cs = scores.items()[:]
            cs.sort(lambda (g1, c1), (g2,c2): -cmp(c1,c2))
            cs = [ c[0] for c in cs ][:5]
            self.hotGames |= set(cs)

    def calculateProperties(self, playsSoFar, ratingsForGames):
        self.calcHotGames(playsSoFar, ratingsForGames)
        self.distinctCount = len(self.played)
        self.daysPlayed = len(self.daysPlayedOn)
        self.newCount = len(self.new)
        self.newNickels = len(self.nickels)
        self.newDimes = len(self.dimes)
        self.newNickelsEver = len(self.everNickels)
        self.newDimesEver = len(self.everDimes)
        self.newQuartersEver = len(self.everQuarters)
        self.newDollarsEver = len(self.everDollars)
        self.newTooltip = makeTooltip(self.new)
        self.newNickelsTooltip = makeTooltip(self.nickels)
        self.newDimesTooltip = makeTooltip(self.dimes)
        self.everNickelsTooltip = makeTooltip(self.everNickels)
        self.everDimesTooltip = makeTooltip(self.everDimes)
        self.everQuartersTooltip = makeTooltip(self.everQuarters)
        self.everDollarsTooltip = makeTooltip(self.everDollars)
        self.distinctTooltip = makeTooltip(self.played)
        self.hotGamesTooltip = makeTooltip(self.hotGames)
        self.expCount = len(self.expPlayed)
        self.expTooltip = makeTooltip(self.expPlayed)
        self.newExpCount = len(self.newExpPlayed)
        self.newExpTooltip = makeTooltip(self.newExpPlayed)
        self.hindex = self.calcHIndex()

    def toMap(self):
        result = Period.toMap(self)
        result["year"] = self.year
        result["month"] = self.month
        result["plays"] = self.plays
        result["count"] = self.count
        result["played"] = list(self.played)
        result["expPlayed"] = list(self.expPlayed)
        result["nickels"] = list(self.nickels)
        result["dimes"] = list(self.dimes)
        result["hotGames"] = list(self.hotGames)
        result["everNickels"] = list(self.everNickels)
        result["everDimes"] = list(self.everDimes)
        result["everQuarters"] = list(self.everQuarters)
        result["everDollars"] = list(self.everDollars)
        result["january"] = self.january
        result["daysPlayedOn"] = set(self.daysPlayedOn)
        result["distinctCount"] = self.distinctCount
        result["daysPlayed"] = self.daysPlayed
        result["newCount"] = self.newCount
        result["newNickels"] = self.newNickels
        result["newDimes"] = self.newDimes
        result["newNickelsEver"] = self.newNickelsEver
        result["newDimesEver"] = self.newDimesEver
        result["newQuartersEver"] = self.newQuartersEver
        result["newDollarsEver"] = self.newDollarsEver
        result["expCount"] = self.expCount
        result["newExpCount"] = self.newExpCount
        result["hindex"] = self.hindex
        return result

class YearToDate(Period):
    def __init__(self, name, opts):
        Period.__init__(self, name, opts)
        self.played = set()
        self.new = set()
        self.newExpPlayed = set()
        self.count = 0

    def toMap(self):
        result = Period.toMap(self)
        result["played"] = list(self.played)
        result["new"] = list(self.new)
        result["newExpPlayed"] = list(self.newExpPlayed)
        result["count"] = self.count
        return result
