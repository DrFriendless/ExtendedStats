import library

allGames = {}

def getGame(id):
    global allGames
    g = allGames.get(id)
    if g is not None:
        return g
    try:
        g = Game(id)
    except NotInDatabase:
        try:
            import populateFiles
            populateFiles.addGame(id)
            g = Game(id)
        except NotInDatabase:
            print "Couldn't add game %d to the database" % id
            return None
    except NoSuchGame:
        return None
    allGames[id] = g
    return g

class NoSuchGame:
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return "NoSuchGame[%s]" % str(self.msg)

class NotInDatabase:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "NotInDatabase[%d]" % self.id

class Game:
    def __init__(self, id):
        self.id = id
        self._readData()
        global allGames
        allGames[id] = self
        import mydb
        db = mydb.get()
        data = library.dbexec(db, "select basegame from expansions where expansion = %d" % self.id)
        self.expansion = len(data) > 0
        if self.expansion:
             self.baseGame = getGame(int(data[0][0]))
        else:
            self.baseGame = None
        data = library.dbexec(db, "select expansion from expansions where basegame = %d" % self.id)
        self.expansions = [ int(x[0]) for x in data ]
        db.close()

    def _readData(self):
        self.playstats = None
        self.totalPlays = 0
        self._readFromDatabase()

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.name

    def _readFromDatabase(self):
        import mydb
        db = mydb.get()
        data = library.dbexec(db, u"select name from games where bggid = %d" % self.id)
        if len(data) == 0:
            raise NotInDatabase(self.id)
        data = data[0]
        self.name = data[0]
        db.close()

    def __cmp__(self, other):
        return cmp(self.name.lower(), other.name.lower())
