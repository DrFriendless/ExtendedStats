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
    data = mydb.query(sql, [geek])
    result = map(__extract(GG_FIELDS, "GeekGame", library.Thing), data)
    return result

GG_FIELDS = ["game", "rating", "owned", "prevowned", "wanttobuy", "wanttoplay", "preordered", "want", "wish", "trade", "comment"]
PLAYS_FIELDS = ["game", "playDate", "quantity", "raters", "ratingsTotal", "location"]
FILES_FIELDS = ["filename", "url", "lastUpdate", "nextUpdate", "processMethod", "tillNextUpdate", "description", "lastattempt"]
GAMES_FIELDS = ["bggid", "name", "average", "rank", "yearpublished", "minplayers", "maxplayers", "playtime", "usersrated",
                "userstrading", "userswanting", "userswishing", "averageweight", "bayesaverage", "stddev", "median",
                "numcomments", "expansion", "usersowned", "subdomain"]
DESIGNER_FIELDS = ["name", "bggid", "boring", "url"]
GAME_DESIGNER_FIELDS = ["gameId", "designerId"]
PUBLISHER_FIELDS = ["name", "bggid", "url"]
GAME_PUBLISHER_FIELDS = ["gameId", "publisherId"]

def __extract(fields, name, constructor):
    def func(row):
        result = constructor(name)
        for i, field in enumerate(fields):
            if isinstance(row[i], str):
                result.__dict__[field] = unicode(row[i], 'utf8')
            else:
                result.__dict__[field] = row[i]
        return result
    return func

def getPlays(geek, start, finish):
    import mydb
    sql = "select " + ",".join(PLAYS_FIELDS) + " from plays where geek = %s order by playDate"
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

def __inlistSQL(fields, table, idField, ids):
    return "select " + ", ".join(fields) + (" from %s where %s in (" % (table, idField)) + ", ".join(map(str,ids)) + ")"

def getGames(ids):
    import mydb
    sql = __inlistSQL(GAMES_FIELDS, "games", "bggid", ids)
    gs = map(__extract(GAMES_FIELDS, "Game", Game), mydb.query(sql))
    for g in gs:
        g.name = g.name.encode('utf-8')
    return { g.bggid : g for g in gs }

class Game(library.Thing):
    def __init__(self, name):
        library.Thing.__init__(self, name)

    def __eq__(self, other):
        return self.bggid == other.bggid

    def __hash__(self):
        return self.bggid

    def __cmp__(self, other):
        return cmp(self.name, other.name)

def getDesigners(ids):
    import mydb, library
    sql = __inlistSQL(DESIGNER_FIELDS, "designers", "bggid", ids)
    gs = map(__extract(DESIGNER_FIELDS, "Designer", library.Thing), mydb.query(sql))
    return { g.bggid : g for g in gs }


def getPublishers(ids):
    import mydb, library
    sql = __inlistSQL(PUBLISHER_FIELDS, "publishers", "bggid", ids)
    gs = map(__extract(PUBLISHER_FIELDS, "Publisher", library.Thing), mydb.query(sql))
    return { g.bggid : g for g in gs }

def getGameDesigners(ids):
    import mydb, library
    sql = __inlistSQL(GAME_DESIGNER_FIELDS, "gameDesigners", "gameId", ids)
    gs = map(__extract(GAME_DESIGNER_FIELDS, "GameDesigner", library.Thing), mydb.query(sql))
    return gs

def getGamePublishers(ids):
    import mydb, library
    sql = __inlistSQL(GAME_PUBLISHER_FIELDS, "gamePublishers", "gameId", ids)
    gs = map(__extract(GAME_PUBLISHER_FIELDS, "GamePublisher", library.Thing), mydb.query(sql))
    return gs

GAME_MECHANIC_FIELDS = ["gameId", "mechanic"]

def getGameMechanics(ids):
    import mydb, library
    sql = __inlistSQL(GAME_MECHANIC_FIELDS, "gameMechanics", "gameId", ids)
    gs = map(__extract(GAME_MECHANIC_FIELDS, "GameMechanic", library.Thing), mydb.query(sql))
    return gs

GAME_CATEGORY_FIELDS = ["gameId", "category"]

def getGameCategories(ids):
    import mydb, library
    sql = __inlistSQL(GAME_CATEGORY_FIELDS, "gameCategories", "gameId", ids)
    gs = map(__extract(GAME_CATEGORY_FIELDS, "GameCategory", library.Thing), mydb.query(sql))
    return gs
