DAY = 24 * 3600

EXPANSION = 1
BASEGAME = 2

def esc(s):
    import MySQLdb
    return MySQLdb.escape_string(s)

class Thing:
    def __init__(self, name="Thing"):
        self.name = name

    def __str__(self):
        # return "%s[%s]" % (self.name, str(self.__dict__))
        return "%s[%s]" % (self.name, "")

    def __repr__(self):
        name = self.name
        dict = self.__dict__
        # return "%s[%s]" % (self.name, str(self.__dict__))
        return "%s[%s]" % (self.name, "")

def between(s, before, after):
    i = s.find(before)
    if i < 0:
        return ""
    s = s[i+len(before):]
    i = s.find(after)
    if i < 0:
        return ""
    s = s[:i]
    return s

BLACK = "#000000"
CYAN = "#00ffff"
PINK = "#ff8888"
RED = "#ff0000"
ORANGE = "#ff8800"
YELLOW = "#ffff00"
GREEN = "#00ff00"
DARKGREEN = "#00bb00"
BLUE = "#0000ff"
DARKBLUE = "#0000bb"
DARKRED = "#bb0000"
INDIGO = "#8800ff"
VIOLET = "#ff88ff"
GREY = "#888888"
GRAY = "#888888"
WHITE = "#ffffff"
DARKGRAY = "#666666"
DARKGREY = "#666666"
YELLOWGREEN = "#aaff00"
BLUEGREEN = "#00aaaa"
LIGHTGREY = "#eeeeee"
LIGHTGRAY = "#dddddd"
LIGHTBLUE = "#add8e6"
LIGHTSALMON = "#FFA07A"
PURPLE = "#800080"
MAGENTA = "#ff00ff"
OLIVE = "#808000"

SPECTRUM = [ PINK, RED, ORANGE, YELLOW, YELLOWGREEN, GREEN, BLUEGREEN, BLUE, INDIGO, VIOLET ]

COLOURS = SPECTRUM + [ BLACK, CYAN, DARKGREEN, DARKBLUE, DARKRED, DARKGRAY, LIGHTBLUE, LIGHTSALMON, PURPLE, MAGENTA, OLIVE ]

def newImage(w=800, h=600, yextra=0, marginProportion=20):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    ylo = img.size[1] / marginProportion
    yhi = img.size[1] - ylo - yextra
    xlo = img.size[0] / marginProportion
    xhi = img.size[0] - xlo
    draw.line([(xlo, ylo), (xlo, yhi)], BLACK)
    draw.line([(xlo, yhi), (xhi, yhi)], BLACK)
    return img, draw, xlo, xhi, ylo, yhi

def playsToColour(plays):
    if plays == 0:
        return WHITE
    elif plays == 1:
        return RED
    elif plays < 3:
        return ORANGE
    elif plays < 5:
        return YELLOW
    elif plays < 10:
        return YELLOWGREEN
    elif plays < 25:
        return GREEN
    else:
        return DARKGREEN

def daysSince(d):
    import datetime
    try:
        if type(d) == type(""):
            fields = [ int(x) for x in d.split("-") ]
            pd = datetime.date(fields[0], fields[1], fields[2])
        else:
            pd = d
    except AttributeError:
        print "daysSince AttributeError", d, type(d)
        return -1
    except ValueError:
        print "COULD NOT PARSE <%s>" % d
        import traceback
        traceback.print_stack()
        return -1
    delta = datetime.date.today() - pd
    return delta.days

def daysBetween(firstDate, lastDate):
    delta = lastDate - firstDate
    m = delta.days
    if m <= 1:
        m = 1
    return m

def yearsBetween(firstDate, lastDate):
    return lastDate.date.year - firstDate.date.year

class DictOfSets:
    def __init__(self):
        self.data = {}

    def add(self, key, value):
        if self.data.get(key) is None:
            self.data[key] = []
        if value not in self.data[key]:
            self.data[key].append(value)

    def addAll(self, key, values):
        for v in values:
            self.add(key, v)

    def __getitem__(self, key):
        if self.data.get(key) is None:
            return []
        return self.data.get(key)

    def get(self, key):
        return self.data.get(key)

    def keys(self):
        return self.data.keys()

class DictOfDicts:
    def __init__(self):
        self.data = {}

    def add(self, key1, key2, value):
        if self.data.get(key1) is None:
            self.data[key1] = {}
        self.data[key1][key2] = value

    def __getitem__(self, key1):
        if self.data.get(key1) is None:
            self.data[key1] = {}
        return self.data[key1]

    def get(self, key1, key2):
        if self.data.get(key1) is None:
            return None
        return self.data.get(key1).get(key2)

    def keys(self):
        ks = self.data.keys()[:]
        ks.sort()
        return ks

class DictOfDictOfLists:
    def __init__(self):
        self.data = {}

    def add(self, key1, key2, value):
        if self.data.get(key1) is None:
            self.data[key1] = DictOfLists()
        self.data[key1].add(key2, value)

    def __getitem__(self, key1):
        if self.data.get(key1) is None:
            self.data[key1] = DictOfLists()
        return self.data[key1]

    def get(self, key1, key2):
        if self.data.get(key1) is None:
            return None
        return self.data[key1][key2]

    def keys(self):
        ks = self.data.keys()[:]
        ks.sort()
        return ks

    def __str__(self):
        return str(self.data)

class DictOfLists:
    def __init__(self):
        self.data = {}

    def add(self, key, value):
        if self.data.get(key) is None:
            self.data[key] = []
        self.data[key].append(value)

    def items(self):
        return self.data.items()

    def __getitem__(self, key):
        if self.data.get(key) is None:
            return []
        return self.data[key]

    def get(self, key):
        return self.data.get(key)

    def keys(self):
        return self.data.keys()

    def addAll(self, dol):
        for (k, vs) in dol.data.items():
            for v in vs:
                self.add(k, v)

    def __len__(self):
        return len(self.data)

    def size(self):
        tot = 0
        for v in self.data.values():
            tot += len(v)
        return tot

    def __repr__(self):
        return `self.data`

    def __str__(self):
        return str(self.data)

class DictOfCounts:
    def __init__(self):
        self.data = {}

    def add(self, key, value, count=1):
        if self.data.get(key) is None:
            self.data[key] = {}
        if self.data[key].get(value) is None:
            self.data[key][value] = 0
        self.data[key][value] += count

    def __getitem__(self, key):
        if self.data.get(key) is None:
            return {}
        return self.data[key]

    def get(self, key):
        return self.data.get(key)

    def getCount(self, key, value):
        if self.data.get(key) is None:
            return 0
        if self.data[key].get(value) is None:
            return 0
        return self.data[key][value]

    def __repr__(self):
        return str(self.data)

    def __str__(self):
        return str(self.data)

    def items(self):
        return self.data.items()[:]

    def keys(self):
        return self.data.keys()[:]

    def __len__(self):
        return len(self.data)

class Counts:
    def __init__(self):
        self.data = {}

    def add(self, key, count=1):
        if self.data.get(key) is None:
            self.data[key] = 0
        self.data[key] += count

    def items(self):
        return self.data.items()[:]

    def asMap(self):
        return self.data.copy()

    def keys(self):
        return self.data.keys()[:]

    def descending(self):
        result = self.data.items()[:]
        result.sort(lambda (k1,v1), (k2,v2): -cmp(v1, v2))
        return [ k for (k,v) in result ]

    def top(self, n):
        result = self.data.items()[:]
        result.sort(lambda (k1,v1), (k2,v2): -cmp(v1, v2))
        return result[:n]

    def __getitem__(self, key):
        if self.data.get(key) is None:
            return 0
        return self.data[key]

    def __delitem__(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return str(self.data)

class AnnotatedCounts(Counts):
    def __init__(self):
        Counts.__init__(self)
        self.annotations = DictOfLists()

    def addAnnotated(self, key, count, anno):
        self.add(key, count)
        self.annotations.add(key, anno)

    def getAnnotations(self, key):
        return self.annotations.get(key)

def dbexec(db, sql, args=None):
    c = db.cursor()
    c.execute(sql, args)
    result = c.fetchall()
    c.close()
    db.commit()
    return result

def getText(node):
    rc = ""
    for node in node.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def beforeSlash(s):
    if s.find("/") < 0:
        return s
    return s[:s.find("/")]

def consecutiveDays(day1, day2):
    return nextday(day1) == day2

def parseDate(yyyydashmmdashdd):
    import datetime
    fields = yyyydashmmdashdd.split('-')
    y = int(fields[0])
    m = int(fields[1])
    d = int(fields[2])
    if y == 0 or m == 0 or d == 0:
        return None
    return datetime.date(y, m, d)

def prevday(d):
    import datetime
    if d.day > 1:
        return datetime.date(d.year, d.month, d.day - 1)
    y = d.year
    m = d.month
    if m == 1:
        m = 12
        y -= 1
    else:
        m -= 1
    for dd in [31, 30, 29, 28]:
        try:
            return datetime.date(y, m, dd)
        except ValueError:
            pass

def nextday(d):
    import datetime
    try:
        return datetime.date(d.year, d.month, d.day + 1)
    except ValueError:
        try:
            return datetime.date(d.year, d.month + 1, 1)
        except ValueError:
            return datetime.date(d.year + 1, 1, 1)

def isToday(d):
    t = d.today()
    return d.day == t.day and d.month == t.month and d.year == t.year

def backToSunday(d):
    while d.weekday() != 6:
        d = prevday(d)
    return d

# exponential distribution cumulative distribution function
def cdf(x,l):
    import math
    return 1.0 - math.exp(-l * float(x))

def invcdf(x, l):
    import math
    return -math.log(1 - float(x)) / l

def average(values):
    if len(values) == 0:
        return 0.0
    return float(sum(values)) / float(len(values))

def uniq(l):
    r = []
    for x in l:
        if x not in r:
            r.append(x)
    return r

def uniquniq(ll):
    r = []
    for l in ll:
        for x in l:
            if x not in r:
                r.append(x)
    return r

def getIDList(nodelist, idkey, func, db):
    result = []
    for node in nodelist:
        id = int(node.getAttribute(idkey))
        name = getText(node.getElementsByTagName("name")[0])
        result.append(func(id, db, name))
    return result

def getRawIDList(nodelist, idkey):
    result = []
    for node in nodelist:
        id = int(node.getAttribute(idkey))
        name = getText(node)
        result.append((id, name))
    return result

def getTextList(nodelist):
    result = []
    for node in nodelist:
        name = getText(node)
        result.append(name)
    return result

def getList(nodelist):
    result = []
    for node in nodelist:
        name = getText(node.getElementsByTagName("name")[0])
        result.append(name)
    return result

def saveRow(db, row, table, where, debug=0):
    count = dbexec(db, "select count(*) from %s where %s" % (table, where))[0][0]
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
        dbexec(db, sql, tuple(args))
    else:
        ds = []
        for i in range(len(vs)):
            ds.append("%s = %s" % (cs[i], vs[i]))
        data = ", ".join(ds)
        sql = "update %s set %s where %s" % (table, data, where)
        if debug:
            print sql
        dbexec(db, sql, tuple(args))

class Row:
    def __init__(self):
        pass

    def items(self):
        return self.__dict__.items()

def findBetween(pos, start, end, s):
    p1 = s.find(start, pos)
    if p1 < 0:
        raise ValueError()
    p2 = s.find(end, p1)
    if p2 < 0:
        raise ValueError()
    p1 += len(start)
    before = s[:p1]
    after = s[p2:]
    middle = s[p1:p2]
    return before, middle, after, p2

def findLinesBetween(lines, start, end):
    result = []
    inside = False
    for l in lines:
        if inside:
            if l.find(end) >= 0:
                return result
            else:
                result.append(l)
        else:
            if l.find(start) >= 0:
                inside = True
    return result

def deleteFileIfBad(filename):
    """Return whether the file exists now or not."""
    import os
    if os.access(filename, os.R_OK):
        with open(filename) as f:
            content = f.read()
            bad1 = (content.find("Addicts may go") > 0) or (content.find("Addicts go") > 0) or (content.find("is down for") > 0) or (content.find("Could not connect to master server") >= 0) or (content.find("server didn't respond") >= 0) or (content.find("server is available") >= 0)
            bad2 = len(content) == 0
        if bad1:
            print "Deleting BGG down file %s" % filename
            os.remove(filename)
            return False
        elif bad2:
            print "Deleting zero length file %s" % filename
            os.remove(filename)
            return False
        return True
    return False

def downloadFile(url, filename):
    import subprocess, time
    try:
        t = time.time()
        subprocess.check_call(["/usr/bin/curl", "--compressed", "-s", "--max-time", "300", "-o", filename, url])
        t2 = time.time()
        print "took", (t2-t)
        return 1
    except subprocess.CalledProcessError:
        print "curl failed to get %s" % url
        return 0

def getFile(url, filename):
    deleteFileIfBad(filename)
    print "Retrieving %s" % url
    url = url.replace(' ', '%20')
    if not downloadFile(url, filename):
        return 0
    return 1

def parsePlaysParams(fields):
    year = None
    month = None
    day = None
    args = []
    stop = False
    for field in fields:
        if not stop and field == "stop":
            stop = True
        elif not stop and (year is None or month is None or day is None):
            try:
                n = int(field)
                if n > 1000 and year is None:
                    year = n
                elif 0 < n < 13 and month is None:
                    month = n
                elif 0 < n < 32 and month is not None and day is None:
                    day = n
            except ValueError:
                args.append(field)
        else:
            args.append(field)
    return year, month, day, args

def getDateRangeForDescribedRange(fields):
    (year, month, day, args) = parsePlaysParams(fields)
    (startDate, endDate) = makeDateRange(year, month, day)
    if "lastyear" in args:
        (startDate, endDate) = makeLastYearDateRange(endDate)
    elif "lastmonth" in args:
        (startDate, endDate) = makeLastMonthDateRange(endDate)
    return year, month, day, args, startDate, endDate

def checkGeek(param, request=None):
    import dbaccess
    username = unicode(param)
    if not username and request is not None:
        username = request.COOKIES.get("username")
        if username is None:
            username = ""
    return dbaccess.checkGeek(username)

def checkGeekGetSelector(param, request, default):
    import selectors
    if param is None:
        username = None
        fields = []
    elif "/" not in param:
        username = unicode(param)
        fields = []
    else:
        fields = param.split("/")
        username = unicode(fields[0])
        fields = fields[1:]
    username = checkGeek(username, request)
    if len(fields) == 0:
        fields = default.split("/")
    selector = selectors.getSelectorFromFields(fields)
    return username, selector

def imageResponse(img):
    from django.http import HttpResponse
    response = HttpResponse(content_type='image/png')
    img.save(response, "PNG")
    return response

def parseYYYYMMDD(dateStr):
    if dateStr is None:
        return None
    import datetime
    fields = dateStr.split("-")
    return datetime.date(int(fields[0]), int(fields[1]), int(fields[2]))

def inlist(lhs, rhs):
    if len(rhs) == 1:
        return "%s = %d" % (lhs, rhs[0])
    else:
        return "%s in (%s)" % (lhs, ",".join(map(str, rhs)))

def strinlist(lhs, rhs):
    if len(rhs) == 1:
        return "%s = '%s'" % (lhs, rhs[0])
    else:
        rhs = [ "'%s'" % s for s in rhs ]
        return "%s in (%s)" % (lhs, ",".join(rhs))

def gameName(g1, g2):
    import locale
    locale.setlocale(locale.LC_COLLATE, "en_US.utf8")
    return locale.strcoll(g1.name, g2.name)

def gameNames(ids, byId):
    strs = []
    for id in ids:
        if byId.get(id) is None:
            strs.append(str(id))
        else:
            strs.append(byId[id].name)
    return ",".join(strs)

def makeDateRange(y, m, d):
    import datetime, calendar
    if y is None:
        return None, None
    elif m is None:
        return datetime.date(y, 1, 1), datetime.date(y, 12, 31)
    elif d is None:
        return datetime.date(y, m, 1), datetime.date(y, m, calendar.monthrange(y,m)[1])
    else:
        return datetime.date(y, m, d), datetime.date(y, m, d)

def makeLastYearDateRange(today):
    import datetime, calendar
    if today is None:
        today = datetime.date.today()
    day = today.day
    if day > calendar.monthrange(today.year-1, today.month)[1]:
        day = calendar.monthrange(today.year-1, today.month)[1]
    start = datetime.date(today.year-1, today.month, day)
    return start, today

def makeLastMonthDateRange(today):
    import datetime, calendar
    if today is None:
        today = datetime.date.today()
    y = today.year
    m = today.month - 1
    if m == 0:
        m = 12
        y -= 1
    day = today.day
    if day > calendar.monthrange(today.year-1, today.month)[1]:
        day = calendar.monthrange(today.year-1, today.month)[1]
    start = datetime.date(y, m, day)
    return start, today

def mean(xs):
    return sum(xs) * 1.0 / len(xs)


def dbTime(dt):
    """convert datetime.time to MYSQL time"""
    import MySQLdb
    return MySQLdb.Timestamp(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

def jsonEncode(obj):
    import datetime, generate, plays, period
    if isinstance(obj, datetime.date):
        return str(obj)
    elif isinstance(obj, Thing):
        return obj.__dict__
    elif isinstance(obj, period.Period) or isinstance(obj, generate.MPTData) or \
            isinstance(obj, plays.Play) or isinstance(obj, generate.DesignerPlaysData):
        return obj.toMap()
    elif isinstance(obj, set):
        return list(obj)
    raise TypeError(obj.__class__.__name__)

class BestFit(object):
    def __init__(self):
        self.sigmaxy = 0.0
        self.sigmax = 0.0
        self.sigmay = 0.0
        self.sigmaxx = 0.0
        self.n = 0
        self.denom = None

    def plot(self, x, y):
        self.sigmaxx += x * x
        self.sigmax += x
        self.sigmay += y
        self.sigmaxy += x * y
        self.n += 1
        self.denom = self.n * self.sigmaxx - self.sigmax * self.sigmax

    def valid(self):
        return self.denom is not None and self.denom != 0

    def a(self):
        return ((self.sigmay * self.sigmaxx) - (self.sigmax * self.sigmaxy)) / self.denom

    def b(self):
        return (self.n * self.sigmaxy - self.sigmax * self.sigmay) / self.denom

    def line(self):
        return self.a(), self.b()

class NoSuchGeekException(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Geek '%s' does not exist" % self.name

def calcHIndex(ns):
    ns.sort(lambda n1,  n2: cmp(n2,  n1))
    h = 0
    while len(ns) > h and ns[h] > h:
        h += 1
    return h