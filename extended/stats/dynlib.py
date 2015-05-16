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
                elif n > 0 and n < 13 and month is None:
                    month = n
                elif n > 0 and n < 32 and month is not None and day is None:
                    day = n
            except ValueError:
                args.append(field)
        else:
            args.append(field) 
    return (year, month, day, args)
    
def getDateRangeForDescribedRange(fields):    
    (year, month, day, args) = parsePlaysParams(fields)    
    (startDate, endDate) = makeDateRange(year, month, day)  
    if "lastyear" in args:
        (startDate, endDate) = makeLastYearDateRange(endDate)
    elif "lastmonth" in args:
        (startDate, endDate) = makeLastMonthDateRange(endDate) 
    return (year, month, day, args, startDate, endDate)

def cdf(x,l):
    import math
    return 1.0 - math.exp(-l * float(x))

def invcdf(x, l):
    import math
    return -math.log(1 - float(x)) / l
    
def checkGeek(param, request=None):
    from models import Geeks
    username = unicode(param)
    if not username and request is not None:
        username = request.COOKIES.get("username")
        if username is None:
            username = ""
    geek = Geeks.objects.get(username=username)
    return (username, geek)
    
def checkGeekGetSelector(param, request, default):
    import selectors
    from models import Geeks
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
    if not username and request is not None:
        username = request.COOKIES.get("username")
        if username is None:
            username = ""
    geek = Geeks.objects.get(username=username)
    if len(fields) == 0:
        fields = default.split("/")                 
    selector = selectors.getSelectorFromFields(fields)
    return (username, geek, selector)
    
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
        return (None, None)
    elif m is None:
        return (datetime.date(y, 1, 1), datetime.date(y, 12, 31))
    elif d is None:
        return (datetime.date(y, m, 1), datetime.date(y, m, calendar.monthrange(y,m)[1]))
    else:
        return (datetime.date(y, m, d), datetime.date(y, m, d))

def makeLastYearDateRange(today):
    import datetime, calendar
    if today is None:
        today = datetime.date.today()
    day = today.day
    if day > calendar.monthrange(today.year-1, today.month)[1]:
        day = calendar.monthrange(today.year-1, today.month)[1]
    start = datetime.date(today.year-1, today.month, day)
    return (start, today)

def makeLastMonthDateRange(today):
    import datetime, calendar
    if today is None:
        today = datetime.date.today()
    y = today.year
    m = today.month - 1
    if m == 0:
        m = 12
        y = y - 1
    day = today.day
    if day > calendar.monthrange(today.year-1, today.month)[1]:
        day = calendar.monthrange(today.year-1, today.month)[1]
    start = datetime.date(y, m, day)
    return (start, today)
    
def mean(xs):
    return sum(xs) * 1.0 / len(xs)

    
def dbTime(dt):    
    "convert datetime.time to MYSQL time"
    import MySQLdb
    return MySQLdb.Timestamp(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
