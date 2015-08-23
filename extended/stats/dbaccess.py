""" A database access layer to replace Django's stuff. """

import library

def checkGeek(name):
    import mydb
    sql = "select username from geeks where username = %s"
    data = mydb.query(sql, [name])
    if len(data) > 0:
        return name
    raise library.NoSuchGeekException(name)

def getAllGeekNames():
    import mydb
    sql = "select username from geeks"
    data = mydb.query(sql)
    return [d[0] for d in data]

def getGeekGamesForGeek(geek):
    import mydb
    sql = "select " + ",".join(GG_FIELDS) + " from geekgames where geek = %s"
    return map(__extract(GG_FIELDS, "GeekGame", library.Thing), mydb.query(sql, [geek]))

GG_FIELDS = ["game", "rating", "owned", "prevowned", "wanttobuy", "wanttoplay", "preordered", "want", "wish", "trade", "comment"]
PLAYS_FIELDS = ["game", "playDate", "quantity", "raters", "ratingsTotal", "location"]
FILES_FIELDS = ["filename", "url", "lastUpdate", "nextUpdate", "processMethod", "tillNextUpdate", "description", "lastattempt"]
GAMES_FIELDS = ["bggid", "name", "average", "rank", "yearpublished", "minplayers", "maxplayers", "playtime", "usersrated",
                "userstrading", "userswanting", "userswishing", "averageweight", "bayesaverage", "stddev", "median",
                "numcomments", "expansion", "usersowned", "subdomain"]

def __extract(fields, name, constructor):
    def func(row):
        result = constructor(name)
        for i in range(len(fields)):
            if isinstance(row[i], str):
                result.__dict__[fields[i]] = unicode(row[i], 'utf8')
            else:
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
    return map(__extract(PLAYS_FIELDS, "Play", library.Thing), mydb.query(sql, args))

def getFilesForGeek(geek):
    import mydb
    sql = "select " + ",".join(FILES_FIELDS) + " from files where geek = %s"
    return map(__extract(FILES_FIELDS, "File", library.Thing), mydb.query(sql, [geek]))

def getGames(ids):
    import mydb
    sql = "select " + ", ".join(GAMES_FIELDS) + " from games where bggid in (" + ", ".join(map(str,ids)) + ")"
    gs = map(__extract(GAMES_FIELDS, "Game", Game), mydb.query(sql))
    return { g.bggid : g for g in gs }

class Game(library.Thing):
    def __init__(self, name):
        library.Thing.__init__(self, name)

    def __eq__(self, other):
        return self.bggid == other.bggid

    def __hash__(self):
        return self.bggid