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
    sql = "select " + ",".join(GG_FIELDS) + " from geekgames where geek = %s"
    return map(__extract(GG_FIELDS), mydb.query(sql, [geek]))

GG_FIELDS = ["game", "rating", "owned", "prevowned", "wanttobuy", "wanttoplay", "preordered", "want", "wish", "trade", "comment"]
PLAYS_FIELDS = ["game", "playDate", "quantity", "raters", "ratingsTotal", "location"]
FILES_FIELDS = ["filename", "url", "lastUpdate", "nextUpdate", "processMethod", "tillNextUpdate", "description", "lastattempt"]

def __extract(fields):
    import library
    def func(row):
        result = library.Thing()
        for i in range(len(fields)):
            result.__dict__[fields[i]] = row[i]
        return result
    return func

def getPlays(geek, start, finish):
    import mydb
    sql = "select " + ",".join(PLAYS_FIELDS) + " from plays where geek = %s"
    args = [geek]
    if start is not None and finish is not None:
        sql += " and playDate between %s and %s"
        args += [start, finish]
    # TODO what if start is None and finish is not, or vice versa?
    return map(__extract(PLAYS_FIELDS), mydb.query(sql, args))

def getFilesForGeek(geek):
    import mydb
    sql = "select " + ",".join(FILES_FIELDS) + " from files where geek = %s"
    return map(__extract(FILES_FIELDS), mydb.query(sql, [geek]))