""" A database access layer to replace Django's stuff. """

class NoSuchGeekException(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Geek '%s' does not exist" % self.name

def checkGeek(name):
    import mydb
    sql = "select username from geeks where username = %s"
    data = mydb.query(sql, [name])
    if len(data) > 0:
        return name
    raise NoSuchGeekException(name)

def getAllGeekNames():
    import mydb
    sql = "select username from geeks"
    data = mydb.query(sql)
    return [d[0] for d in data]

def getGeekGamesForGeek(geek):
    import mydb
    sql = "select game, rating, owned, prevowned, wanttobuy, wanttoplay, preordered, want, wish, trade, comment from geekgames where geek = %s"
    data = mydb.query(sql, [geek])
    return map(__extractGeekGame, data)

GG_FIELDS = ["game", "rating", "owned", "prevowned", "wanttobuy", "wanttoplay", "preordered", "want", "wish", "trade", "comment"]
def __extractGeekGame(row):
    import library
    result = library.Thing()
    for i in range(len(GG_FIELDS)):
        #result[GG_FIELDS[i]] = row[i]
        result.__dict__[GG_FIELDS[i]] = row[i]
    return result