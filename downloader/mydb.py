import sitedata

class MyDB(object):
    def __init__(self):
        import MySQLdb
        self.db = MySQLdb.connect(host=sitedata.dbhost, user=sitedata.dbuser , passwd=sitedata.password, db=sitedata.dbname)
        self.db.autocommit = True
        self.db.set_character_set('utf8')
        dbc = self.db.cursor()
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')
        dbc.close()
        self.db.optimised = False 
        
    def execute(self, sql, args=None):
        c = self.db.cursor()
        c.execute(sql, args)
        result = c.fetchall()
        c.close()
        self.db.commit()
        return result

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()
        
    def saveRow(self, row, table, where, debug=0):
        count = self.execute("select count(*) from %s where %s" % (table, where))[0][0]
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
            self.execute(sql, tuple(args))
        else:
            ds = []
            for i in range(len(vs)):
                ds.append("%s = %s" % (cs[i], vs[i]))
            data = ", ".join(ds)
            sql = "update %s set %s where %s" % (table, data, where)
            if debug:
                print sql
            self.execute(sql, tuple(args))

class Row:
    def __init__(self):
        pass

    def items(self):
        return self.__dict__.items()
