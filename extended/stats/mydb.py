TESTING = False

def get():
    import sitedata
    if TESTING:
        import sqlite3
        db = sqlite3.connect(":memory:")
    else:
        import MySQLdb
        db = MySQLdb.connect(host=sitedata.dbhost, user=sitedata.dbuser , passwd=sitedata.password, db=sitedata.dbname)
        db.autocommit = True
        #db.set_character_set('utf8')
        dbc = db.cursor()
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')
        #dbc.execute("SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''))")
        #dbc.execute("SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'NO_ZERO_DATE',''))")
        dbc.close()
        db.optimised = False
    return db

def query(sql, args=None):
    db = get()
    dbc = db.cursor()
    if type(args) in [type(""), type(u"")]:
        args = [args]
    dbc.execute(sql, args)
    result = dbc.fetchall()
    dbc.close()
    db.close()
    return result

def update(sql, args=None):
    db = get()
    c = db.cursor()
    c.execute(sql, args)
    result = c.fetchall()
    c.close()
    db.commit()
    db.close()
    return result

def updateDb(db, sql, args=None):
    c = db.cursor()
    c.execute(sql, args)
    result = c.fetchall()
    c.close()
    return result

def saveRowDb(db, row, table, where, debug=0):
    if where is not None:
        count = query("select count(*) from %s where %s" % (table, where))[0][0]
    else:
        count = 0
    cs = []
    vs = []
    args = []
    for (col, val) in row.items():
        cs.append(col)
        if type(val) == type(""):
            vs.append("%s")
            args.append(val)
        elif type(val) == type(u""):
            vs.append("%s")
            args.append(val.encode('utf8'))
        else:
            vs.append(str(val))
    cols = ", ".join(cs)
    vals = ", ".join(vs)
    if count == 0:
        sql = "insert into %s (%s) values (%s)" % (table, cols, vals)
        if debug:
            print sql
        updateDb(db, sql, tuple(args))
    else:
        ds = []
        for i, v in enumerate(vs):
            ds.append("%s = %s" % (cs[i], v))
        data = ", ".join(ds)
        sql = "update %s set %s where %s" % (table, data, where)
        if debug:
            print sql
        updateDb(db, sql, tuple(args))


def saveRow(row, table, where, debug=0):
    if where is not None:
        count = query("select count(*) from %s where %s" % (table, where))[0][0]
    else:
        count = 0
    cs = []
    vs = []
    args = []
    for (col, val) in row.items():
        cs.append(col)
        if type(val) == type(""):
            vs.append("%s")
            args.append(val)
        elif type(val) == type(u""):
            vs.append("%s")
            args.append(val.encode('utf8'))
        else:
            vs.append(str(val))
    cols = ", ".join(cs)
    vals = ", ".join(vs)
    if count == 0:
        sql = "insert into %s (%s) values (%s)" % (table, cols, vals)
        if debug:
            print sql
        update(sql, tuple(args))
    else:
        ds = []
        for (index,v) in enumerate(vs):
            ds.append("%s = %s" % (cs[index], v))
        data = ", ".join(ds)
        sql = "update %s set %s where %s" % (table, data, where)
        if debug:
            print sql
        update(sql, tuple(args))

