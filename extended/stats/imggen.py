from library import *
IGNORE = ["atarist", "android", "nes", "pc", None]
FLORENCE_COLOURS = { None: '#ffffff', 'abstracts' : '#000000', 'boardgame' : '#20b020', 'cgs': '#d060d0',
                     'childrensgames' : '#f0d000', 'familygames': '#20d0d0', 'partygames': '#f02020',
                     'strategygames': '#4381b2', 'thematic' : '#fab6b6', 'wargames' : '#BDB76B', 'android' : "#A4C639" }
FLORENCE_ANGLE = 30
FLORENCE_CATS = []
PIE_SIZE = 200
ALDIES_COLOURS = [ '#ff0000', '#ff3366', '#ff6699', '#ff66cc', '#cc99ff', '#9999ff', '#99ffff',
                   '#66ff99', '#33cc99', '#00cc00']
MIKE_HULSEBUS_COLOURS = ["#ff420e", "#ffd320", "#569d1b", "#7d0020", "#83cafe", "#324005", "#aed000",
                         "#4a1f6f", "#fd950e", "#c5000a", "#0083d1", "#004586" ]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
GAME_PLAYS_URL = "http://boardgamegeek.com/plays/thing/%d?userid=%d"
BGG_PLAYS_URL = "http://boardgamegeek.com/collection/user/%s?own=1&minplays=%d&maxplays=%d"
BGG_ZERO_PLAYS_URL = "http://boardgamegeek.com/collection/user/%s?own=1&played=0"
import library
CLOSENESS = library.DictOfDicts()

def escape(s):
    return unicode(s.replace("'", "\\'"))

def getFlorenceCats():
    import mydb
    sql = "select distinct subdomain from games order by 1"
    cats = mydb.query(sql)
    return [c[0] for c in cats if c[0]not in IGNORE]

def getFlorenceSettings():
    import library
    result = []
    cats = getFlorenceCats()
    for cat in cats:
        t = library.Thing()
        t.colour = FLORENCE_COLOURS[cat]
        t.name = cat
        result.append(t)
    return result


def centreText(draw, s, x1, x2, y):
    w = draw.textsize(s)[0]
    l = (x2 - x1 - w)/2
    draw.text((x1+l, y), s, fill=BLACK)

def createNewPlaysGraph(context,  data):
    """graph of new plays accumulating over time, and over years"""
    # data is a list of dates
    import library, datetime, math
    imgspec = context.imageSpec
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, imgspec.height, 0, 10)
    countPlaysByYear = library.Counts()
    for date in data:
        countPlaysByYear.add(date.year)
    data.sort()
    minYear = None
    maxYear = None
    if len(countPlaysByYear) > 0:
        maxYear = library.TODAY.year
        while countPlaysByYear[maxYear] == 0:
            maxYear -= 1
        minYear = maxYear
        while countPlaysByYear[minYear-1] > 0:
            minYear -= 1
    if minYear is not None and maxYear is not None:
        oneDay = datetime.timedelta(1)
        startDate = datetime.date(minYear, 1, 1)
        endDate = datetime.date(library.TODAY.year, 12, 31)
        data = [ d for d in data if startDate <= d <= endDate ]
        widthInDays = (endDate - startDate).days
        daysX = 0
        curDate = startDate
        newGamesPerYear = {}
        index = 0
        yearTrails = []
        allTimeTrail = []
        allTime = 0
        while curDate <= endDate:
            if len(data) == index:
                break
            if newGamesPerYear.get(curDate.year) is None:
                newGamesPerYear[curDate.year] = 0
            found = False
            while index < len(data) and curDate.toordinal() == data[index].toordinal():
                newGamesPerYear[curDate.year] += 1
                allTime += 1
                index += 1
                found = True
            if found:
                yearTrails.append((daysX, newGamesPerYear[curDate.year]))
                allTimeTrail.append((daysX, allTime))
            curDate = curDate + oneDay
            daysX += 1
        maxInOneYear = max(newGamesPerYear.values())
        maxInOneYear = math.ceil(maxInOneYear/10.0) * 10
        allTime = math.ceil(allTime/100.0) * 100
        def convY(dy, my):
            return int(yhi - (yhi - ylo) * dy / my)
        def convX(dx):
            return int(xlo + (xhi - xlo) * dx / widthInDays)
        curYear = startDate.year
        while curYear <= endDate.year:
            jan1 = datetime.date(curYear, 1, 1)
            jan1NextYear = datetime.date(curYear+1, 1, 1)
            x1 = int(xlo + (xhi - xlo) * (jan1 - startDate).days / widthInDays)
            if x1 == xlo:
                x1 += 1
            x2 = int(xlo + (xhi - xlo) * (jan1NextYear - startDate).days / widthInDays)
            centreText(draw, str(curYear), x1, x2, yhi + 10)
            if curYear % 2 == 1:
                draw.rectangle([(x1, ylo), (x2, yhi-1)], fill=YELLOWGREEN)
            curYear += 1
        ly = 0
        while ly <= maxInOneYear:
            y = convY(ly, maxInOneYear)
            draw.line([xlo-5, y, xlo, y], BLACK)
            if 0 < ly < maxInOneYear:
                draw.text((xlo-30, y-10), str(ly), fill=BLACK)
                draw.line([xlo, y, xhi, y], DARKGRAY)
            ly += 10
        ry = 0
        while ry <= allTime:
            y = convY(ry, allTime)
            draw.line([xhi+5, y, xhi, y], BLUE)
            if 0 < ry < allTime:
                draw.text((xhi+10, y-10), str(ry), fill=BLUE)
            ry += 50
        for (dx, dy) in yearTrails:
            x = convX(dx)
            y = convY(dy, maxInOneYear)
            draw.ellipse((x-2,y-2, x+2, y+2), fill=BLACK)
        for (dx, dy) in allTimeTrail:
            x = convX(dx)
            y = convY(dy, allTime)
            draw.polygon([(x-2,y+1), (x, y-1), (x+2,y+1)], outline=BLUE)
    del draw
    return img

def createLagHistogram(context,  data):
    """histogram of years since game was released till date of first play"""
    # data is a library.Counts with keys of years since game published  
    imgspec = context.imageSpec
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, imgspec.height)
    data = data.asMap()
    top = 0
    max = 1
    total = 0
    for (k,  v) in data.items():
        if k >= 20:
            top = top + v
            if top > max:
                max = top
        if v > max:
            max = v
        total = total + v
    data[20] = top
    accum = 0
    shade = False
    for key in range(21):
        x1 = xlo + (xhi - xlo) * key / 21
        x2 = xlo + (xhi - xlo) * (key+1) / 21
        v = data.get(key)
        if v is None:
            v = 0
        y = yhi - (yhi - ylo) * v / max
        bg = WHITE
        if shade:
            bg = LIGHTBLUE
        draw.rectangle([(x1, yhi), (x2,  y)], outline=BLACK,  fill=bg)
        centreText(draw, str(key), x1, x2, yhi+10)
        centreText(draw, str(v), x1, x2, (y+yhi)/2)
        accum = accum + v
        draw.rectangle([(x1, ylo-1), (x2, ylo-16)], fill=bg)
        if total > 0:
            centreText(draw, str(int(accum*100/total))+"%", x1, x2, ylo-14)
        shade = not shade
    del draw
    return img

def __sortLifetime(d1, d2):
    n = -cmp(d1[0], d2[0])
    if n == 0:
        n = cmp(d1[1], d2[1])
        if n == 0:
            n = cmp(d1[2], d2[2])
    return n

def createLifetimeGraph(context,  data):
    "histogram of days between first play and last play"
    # data is a list of (int, boolean, boolean) triples, where
    # int is days between plays 
    # boolean is whether expansion or not
    # boolean is whether owned or not
    imgspec = context.imageSpec
    height = imgspec.height
    if height < len(data):
        height = len(data)
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, height)
    data.sort(__sortLifetime)
    numGames = len(data)
    ages = [ d[3] for d in data ]
    ages.sort(lambda g1, g2: -cmp(g1, g2))
    if len(data) > 0:
        max = data[0][0]
        if max > 3652:
            max = 3652
        xd = 0
        while xd <= max:
            x = xlo + (xhi - xlo) * xd / max
            x2 = xlo + (xhi - xlo) * (xd+200) / max
            if x2 > xhi:
                x2 = xhi
            draw.line([x, yhi, x, yhi+5], BLACK, 1)
            if xd % 400 == 0:
                draw.rectangle([(x, yhi), (x2, ylo)], fill=LIGHTGRAY)
            draw.text((x, yhi + 20), str(xd), fill=BLACK)
            draw.text((x, ylo - 20), str(xd), fill=BLACK)
            xd += 200
        yd = 0
        while yd <= 100:
            y = yhi - (yhi - ylo) * yd / 100
            draw.line([xlo-5, y, xlo, y], fill=BLACK)
            draw.text((xlo-30, y-10), "%d%%" % yd, fill=BLACK)
            n = numGames * yd / 100
            draw.text((xlo-35, y+3), "(%d)" % n, fill=BLACK)
            yd += 10
        index = 0
        for (days, expansion, own, age) in data:
            #age = ages[index]
            if days > 3652:
                days = 3652
            x = xlo + (xhi - xlo) * days / max
            y1 = yhi - (index * (yhi - ylo) / numGames)
            y2 = yhi - ((index+1) * (yhi - ylo) / numGames)
            index += 1
            if expansion and own:
                colour = YELLOW
            elif expansion:
                colour = BLUE
            elif own:
                colour = DARKGREEN
            else:
                colour = LIGHTSALMON
            draw.rectangle([(xlo, y1), (x, y2)], fill=colour)
            if age < 3652:
                x = xlo + (xhi - xlo) * age / max
                draw.rectangle([(x, y1), (x+1, y2)], fill=BLACK)
    del draw
    return img

def createLifetimeByRatingGraph(context,  data):
    "histogram of days between first play and last play coloured by rating"
    # data is a list of (int, rating) triples, where
    # int is days between plays 
    # rating is rating given by the user on BGG
    imgspec = context.imageSpec
    height = imgspec.height
    if height < len(data):
        height = len(data)
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, height)
    data.sort(lambda g1, g2: -cmp(g1[0], g2[0]))
    numGames = len(data)
    if len(data) > 0:
        max = data[0][0]
        if max > 3652:
            max = 3652
        xd = 0
        while xd <= max:
            x = xlo + (xhi - xlo) * xd / max
            x2 = xlo + (xhi - xlo) * (xd+200) / max
            if x2 > xhi:
                x2 = xhi
            draw.line([x, yhi, x, yhi+5], BLACK, 1)
            if xd % 400 == 0:
                draw.rectangle([(x, yhi), (x2, ylo)], fill=LIGHTGRAY)
            draw.text((x, yhi + 20), str(xd), fill=BLACK)
            draw.text((x, ylo - 20), str(xd), fill=BLACK)
            xd += 200
        yd = 0
        while yd <= 100:
            y = yhi - (yhi - ylo) * yd / 100
            draw.line([xlo-5, y, xlo, y], fill=BLACK)
            draw.text((xlo-30, y-10), "%d%%" % yd, fill=BLACK)
            n = numGames * yd / 100
            draw.text((xlo-35, y+3), "(%d)" % n, fill=BLACK)
            yd += 10
        index = 0
        for (days, rating) in data:
            if days > 3652:
                days = 3652
            x = xlo + (xhi - xlo) * days / max
            y1 = yhi - (index * (yhi - ylo) / numGames)
            y2 = yhi - ((index+1) * (yhi - ylo) / numGames)
            index += 1
            colour = getAldiesColour(rating)
            draw.rectangle([(xlo, y1), (x, y2)], fill=colour)
    del draw
    return img

def createFlorenceDiagram(geek, data):
    import math
    cats = getFlorenceCats()
    floc = [ math.sqrt(data[cats[slice]] * 80.0) for slice in range(len(cats)) ]
    from PIL import Image, ImageDraw
    SIDE = 320
    MID = SIDE / 2
    if max(floc) > MID - 10:
        MID = int(max(floc)) + 10
        SIDE = MID * 2
    img = Image.new("RGB", (SIDE, SIDE), WHITE)
    draw = ImageDraw.Draw(img)
    PER_SLICE = 360.0 / len(cats)
    HALF = (PER_SLICE - FLORENCE_ANGLE) / 2.0
    for slice in range(len(cats)):
        start = HALF + slice * PER_SLICE
        end = start + FLORENCE_ANGLE
        radius = int(floc[slice])
        xy = (MID - radius, MID - radius, MID + radius, MID + radius)
        draw.pieslice(xy, int(start), int(end), FLORENCE_COLOURS[cats[slice]], outline=BLACK)
    del draw
    return img

def createPBMGraph(context, data):
    months = len(data)
    from PIL import Image, ImageDraw
    WIDTH = 30
    HEIGHT = 300
    xlo = 50
    xhi = xlo + WIDTH * months
    ylo = 50
    yhi = 250
    img = Image.new("RGB", (xhi + 25, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    divs = 10
    if len(data) > 0:
        maxy = max([d.count for d in data])
        if maxy > 200:
            divs = 20
        by = 0
        while by < maxy+divs:
            y = (yhi - ylo) * by / maxy
            draw.line([xlo, yhi - y, xhi, yhi - y], DARKGRAY, 1)
            draw.text((xlo-20, yhi-y-10), str(by), fill=BLACK)
            by += divs
        x = xlo
        for m in data:
            y = (yhi - ylo) * m.count / maxy
            draw.rectangle([(x, yhi), (x + WIDTH - 1, yhi - y)], fill=DARKGREEN)
            y = (yhi - ylo) * m.distinctCount / maxy
            draw.rectangle([(x, yhi), (x + WIDTH - 1, yhi - y)], fill=DARKBLUE)
            y = (yhi - ylo) * m.newCount / maxy
            draw.rectangle([(x, yhi), (x + WIDTH - 1, yhi - y)], fill=DARKRED)
            draw.text((x, yhi + 10), MONTH_NAMES[m.month-1], fill=BLACK)
            draw.text((x, yhi + 20), str(m.year), fill=BLACK)
            x += WIDTH
    del draw
    return img

def createGiniGraph(context, data):
    (img, draw, xlo, xhi, ylo, yhi) = newImage(400, 300)
    draw.polygon([(xlo, yhi), (xhi, ylo), (xhi, yhi)], outline=BLACK, fill="#b0c4d6")
    draw.line([(xlo, ylo), (xlo, yhi)], WHITE)
    draw.line([(xhi, ylo), (xhi, yhi)], BLACK)
    points = [(xlo, yhi)]
    totalPlays = data[0].totalPlays
    playsSoFar = 0
    i = 0
    imap = []
    for gg in data:
        x1 = xlo + (xhi - xlo) * i / len(data)
        i += 1
        playsSoFar += gg.plays
        x2 = xlo + (xhi - xlo) * i / len(data)
        y = yhi - (yhi - ylo) * playsSoFar / totalPlays
        points.append((x1,y))
        points.append((x2,y))
        mapRow = Thing()
        (mapRow.x1, mapRow.y1, mapRow.x2, mapRow.y2) = (x1, yhi, x2, ylo)
        mapRow.title = gg.name
        imap.append(mapRow)
    draw.polygon(points, outline=BLACK, fill="#80b3ff")
    del draw
    return img, imap

def createPogoHistogram(context, data):
    count = {}
    expansions = {}
    titles = {}
    etitles = {}
    imap = []
    maxi = 28
    for c in range(maxi):
        count[c] = 0
        expansions[c] = 0
        titles[c] = []
        etitles[c] = []
    maxcount = 1
    tens = 0
    for gg in data:
        if gg.plays >= 10:
            tens += 1
        if gg.plays >= 100:
            gg.plays = 27
        elif gg.plays >= 50:
            gg.plays = 26
        elif gg.plays >= 25:
            gg.plays = 25
        count[gg.plays] += 1
        if count[gg.plays] > maxcount:
            maxcount = count[gg.plays]
        if gg.expansion:
            expansions[gg.plays] += 1
            if etitles.get(gg.plays) is None:
                etitles[gg.plays] = []
            etitles[gg.plays].append(gg.name)
        else:
            if titles.get(gg.plays) is None:
                titles[gg.plays] = []
            titles[gg.plays].append(gg.name)
    imgspec = context.imageSpec
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, imgspec.height)
    for p in range(maxi):
        ymin = ylo + (maxi - 1 - p) * (yhi - ylo) / maxi
        ymax = ylo + (maxi - p) * (yhi - ylo) / maxi
        x1 = xlo + (xhi - xlo) * expansions[p] / maxcount
        x2 = xlo + (xhi - xlo) * count[p] / maxcount
        h = ymax - ymin
        y1 = ymin + h/4
        y2 = ymax - h/4
        if p >= 10:
            cols = (LIGHTBLUE, BLUEGREEN)
        elif p == 0:
            cols = (LIGHTSALMON, VIOLET)
        draw.rectangle([(x1, y1), (x2, y2)], outline=BLACK, fill=cols[0])
        if expansions[p] > 0:
            draw.rectangle([(xlo, y1), (x1, y2)], outline=BLACK, fill=cols[1])
            #draw.rectangle([(xlo, y1), (x2, y2)], outline=BLACK)
        (mi, ma) = (p, p)
        if p == 25:
            (mi, ma) = (25, 49)
        elif p == 26:
            (mi, ma) = (50, 99)
        elif p == maxi - 1:
            (mi, ma) = (100, 1000000)
        url = BGG_PLAYS_URL % (context.geek, mi, ma)
        if p == 0:
            url = BGG_ZERO_PLAYS_URL % context.geek
        mapRow = Thing()
        (mapRow.x1, mapRow.y1, mapRow.x2, mapRow.y2) = (x1, y1, x2, y2)
        mapRow.url = url
        if titles.get(p) is None:
            titles[p] = []
        mapRow.title = ", ".join(titles[p])
        imap.append(mapRow)
        if expansions[p] > 0:
            mapRow = Thing()
            (mapRow.x1, mapRow.y1, mapRow.x2, mapRow.y2) = (xlo, y1, x1, y2)
            mapRow.url = url
            mapRow.title = ", ".join(etitles[p])
            imap.append(mapRow)
        if 0 <= tens < count[p]:
            fm = count[p] - tens
            xt = xlo + (xhi - xlo) * fm / maxcount
            draw.line([xt, y1-2, xt, y2+2], GREEN, 1)
        text = str(p)
        if text == "27":
            text = "100+"
        elif text == "26":
            text = "50-99"
        elif text == "25":
            text = "25-49"
        draw.text((5, y1), text, fill=BLACK)
        draw.text((x2 + 5, y1), str(count[p]), fill=GREY)
        tens = tens - count[p]
    draw.text((25, 5), "Histogram of Count of Number of Games Owned with each Number of Plays", fill=BLACK)
    del draw
    return img, imap

def getAldiesColour(rating):
    import math
    r = int(math.floor(rating + 0.5))
    if 0 < r <= 10:
        return ALDIES_COLOURS[r-1]
    return None

def createFirstPlayVsRatingGraph(context, data, years):
    import library, time, datetime
    imgspec = context.imageSpec
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, imgspec.height)
    for rating in range(1, 10, 2):
        y1 = yhi + int(float(rating * (ylo - yhi) / 10.0))
        y2 = yhi + int(float((rating + 1) * (ylo - yhi) / 10.0))
        draw.rectangle([xlo+1, y1, xhi, y2], fill=LIGHTGREY)
    for rating in range(1,11):
        y = yhi + int(float(rating * (ylo - yhi) / 10.0))
        draw.text((xlo-15, y-4), str(rating), fill=BLACK)
    if len(years) > 0:
        minYear = min(years)
        endYear = time.localtime()[0]
        data = [ d for d in data if d[1] is not None and d[1].year >= minYear ]
        bf = library.BestFit()
        radius = 3
        if len(data) > 0:
            minDate = data[0][1]
            maxDate = data[-1][1]
            days = (maxDate - minDate).days * 1.0
            for d in data:
                p = (d[1] - minDate).days / days
                x = xlo + int(p * (xhi - xlo))
                y = yhi + int(float(d[2]) * (ylo - yhi) / 10.0)
                bf.plot(x-xlo, y-yhi)
                draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], outline=BLACK)
            if bf.valid():
                (a, b) = bf.line()
                draw.line([(xlo, yhi + a), (xhi, yhi + a + b * (xhi-xlo))], CYAN, 1)
            y = minYear
            while y <= endYear:
                jan1 = datetime.date(y, 1, 1)
                if jan1 >= minDate:
                    p = (jan1 - minDate).days / days
                    x = xlo + int(p * (xhi - xlo))
                    draw.line([x, ylo, x, yhi], DARKGREY)
                    draw.text((x, yhi + 10), str(y), fill=BLACK)
                y += 1
    del draw
    return img

def createRatingByPublishedYearGraph(context, data, upsideDown):
    import time, math
    startYear = 1995
    endYear = time.localtime()[0]
    yearData = {}
    year = startYear
    while year <= endYear:
        yearData[year] = { 1: 0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0 }
        year += 1
    for (count, r, year) in data:
        if yearData.get(year) is None:
            continue
        r2 = math.floor(r)
        if r2 < 1:
            r2 = 1
        if r2 > 10:
            r2 = 10
        yearData[year][r2] = yearData[year][r2] + count
    imgspec = context.imageSpec
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, imgspec.height)
    imap = []
    highest = max([sum(yearData[year].values()) for year in yearData.keys()])
    year = startYear
    while year <= endYear:
        x0 = xlo + ((year - startYear) * (xhi - xlo) * 1.0 / (endYear + 1 - startYear))
        x1 = xlo + ((year + 1 - startYear) * (xhi - xlo) * 1.0 / (endYear + 1 - startYear))
        soFar = 0
        if highest > 0:
            ra = range(1, 11)
            if upsideDown:
                ra.reverse()
            for r in ra:
                v = yearData[year][r]
                y0 = yhi - int(soFar * 1.0 * (yhi - ylo) / highest)
                soFar = soFar + v
                y1 = yhi - int(soFar * 1.0 * (yhi - ylo) / highest)
                if y1 == y0:
                    continue
                draw.rectangle([x0, y0, x1, y1], outline=BLACK, fill=ALDIES_COLOURS[r-1])
                mapRow = Thing()
                (mapRow.x1, mapRow.y1, mapRow.x2, mapRow.y2) = (int(x0), int(y1), int(x1), int(y0))
                mapRow.name = str(int(v))
                mapRow.url = None
                imap.append(mapRow)
        draw.text((x0+10, yhi+7), str(year), fill=BLACK)
        draw.text((x0+15, ylo-14), str(sum(yearData[year].values())), fill=BLACK)
        year += 1
    del draw
    return img, imap

def createOwnedByPublishedYearGraph(context, data, upsideDown):
    import time, math
    startYear = 1995
    endYear = time.localtime()[0]
    yearData = {}
    year = startYear
    while year <= endYear:
        yearData[year] = { -1: 0, 1: 0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0 }
        year += 1
    for (count, r, year) in data:
        if yearData.get(year) is None:
            continue
        r2 = math.floor(r)
        if r2 < 1:
            r2 = -1
        if r2 > 10:
            r2 = 10
        yearData[year][r2] = yearData[year][r2] + count
    imgspec = context.imageSpec
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, imgspec.height)
    imap = []
    highest = max([sum(yearData[year].values()) for year in yearData.keys()])
    year = startYear
    while year <= endYear:
        x0 = xlo + ((year - startYear) * (xhi - xlo) * 1.0 / (endYear + 1 - startYear))
        x1 = xlo + ((year + 1 - startYear) * (xhi - xlo) * 1.0 / (endYear + 1 - startYear))
        soFar = 0
        if highest > 0:
            ras = [-1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            if upsideDown:
                ras.reverse()
            for rating in ras:
                v = yearData[year][rating]
                y0 = yhi - int(soFar * 1.0 * (yhi - ylo) / highest)
                soFar = soFar + v
                y1 = yhi - int(soFar * 1.0 * (yhi - ylo) / highest)
                if rating <= 0:
                    fill = WHITE
                else:
                    fill = ALDIES_COLOURS[rating-1]
                if y1 == y0:
                    continue
                draw.rectangle([x0, y0, x1, y1], outline=BLACK, fill=fill)
                mapRow = Thing()
                (mapRow.x1, mapRow.y1, mapRow.x2, mapRow.y2) = (int(x0), int(y1), int(x1), int(y0))
                mapRow.name = str(int(v))
                mapRow.url = None
                imap.append(mapRow)
        draw.text((x0+10, yhi+7), str(year), fill=BLACK)
        draw.text((x0+20, ylo-14), str(sum(yearData[year].values())), fill=BLACK)
        year += 1
    del draw
    return img, imap

def createPlaysByPublishedYearGraph(context, data, upsideDown):
    import time, mydb
    startYear = 1995
    endYear = time.localtime()[0]
    years = []
    year = startYear
    while year <= endYear:
        years.append(year)
        if data.get(year) is None:
            data.data[year] = []
        year += 1
    sizes = [ len(data[y]) for y in years ]
    sql = "select bggid from users where geek = %s"
    geekData = mydb.query(sql, context.geek)
    try:
        bggid = geekData[0][0]
    except IndexError:
        bggid = 0
    imgspec = context.imageSpec
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, imgspec.height)
    imap = []
    highest = max(sizes)
    year = startYear
    height = 1.0 * (yhi - ylo)
    while year <= endYear:
        x0 = xlo + ((year - startYear) * (xhi - xlo) * 1.0 / (endYear + 1 - startYear))
        x1 = xlo + ((year + 1 - startYear) * (xhi - xlo) * 1.0 / (endYear + 1 - startYear))
        data[year].sort(lambda g1, g2: cmp(g1.plays, g2.plays))
        if upsideDown:
            data[year].reverse()
        if highest > 0:
            count = 0
            for g in data[year]:
                y0 = yhi - int(count * height / highest)
                count += 1
                y1 = yhi - int(count * height / highest)
                if g.plays == 0:
                    fill = WHITE
                elif g.plays == 1:
                    fill = RED
                elif g.plays < 3:
                    fill = ORANGE
                elif g.plays < 5:
                    fill = YELLOW
                elif g.plays < 10:
                    fill = YELLOWGREEN
                elif g.plays < 25:
                    fill = GREEN
                else:
                    fill = DARKGREEN
                if y1 == y0:
                    continue
                draw.rectangle([x0, y0, x1, y1], outline=BLACK, fill=fill)
                mapRow = Thing()
                (mapRow.x1, mapRow.y1, mapRow.x2, mapRow.y2) = (int(x0), int(y1), int(x1), int(y0))
                mapRow.name = escape(g.name)
                mapRow.url = None
                if bggid:
                    mapRow.url = GAME_PLAYS_URL % (g.bggid, bggid)
                imap.append(mapRow)
        draw.text((x0+10, yhi+7), str(year), fill=BLACK)
        draw.text((x0+20, ylo-14), str(len(data[year])), fill=BLACK)
        year += 1
    del draw
    return img, imap

def createPlayRateGraph(context, (data, names)):
    import math
    counts = [ [ 0 for x in range(26) ] for y in range(11) ]
    tots = [ 0 for x in range(11) ]
    for numPlays in data.keys():
        numGamesForRatings = data[numPlays]
        for (rating, numGames) in numGamesForRatings.items():
            if rating < 0:
                rating = 0
            tots[rating] = tots[rating] + numGames * numPlays
            counts[rating][numPlays] = counts[rating][numPlays] + numGames
    imgspec = context.imageSpec
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, imgspec.height)
    imap = []
    for p in range(26):
        y = ylo + (yhi - ylo) * (25 - p) / 25.0
        draw.text((5, y-4), str(p), fill=BLACK)
    for r in range(0, 11):
        x = xlo + (xhi - xlo) * r / 10.0
        draw.text((x, img.size[1] - 15), str(r), fill=BLACK)
    for plays in range(26):
        for rating in range(0, 11):
            n = counts[rating][plays]
            if n == 0:
                continue
            radius = math.sqrt(10 * n)
            x = xlo + (xhi - xlo) * rating / 10.0
            y = ylo + (yhi - ylo) * (25 - plays) / 25.0
            col = GREY
            if plays >= 10:
                col = CYAN
            elif plays == 0:
                col = RED
            row = Thing()
            row.x = x
            row.y = y
            row.radius = radius
            row.name = ", ".join(names.get(plays, rating)).replace("'", "")
            imap.append(row)
            draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], outline=BLACK, fill=col)
    prev = None
    for rating in range(0, 11):
        c = sum(counts[rating]) * 1.0
        if c == 0:
            continue
        tot = tots[rating] * 1.0
        x = xlo + (xhi - xlo) * rating / 10.0
        y = ylo + (yhi - ylo) * (25 - (tot / c)) / 25.0
        draw.line([x-2, y-2, x+2, y+2], GREEN, 1)
        draw.line([x-2, y+2, x-2, y+2], GREEN, 1)
        if prev is not None:
            draw.line([prev[0], prev[1], x, y], GREEN, 1)
        prev = (x, y)
    draw.text((25, 5), "Scatter Plot of Number of Plays vs Rating", fill=BLACK)
    del draw
    return img, imap

def createPlaysForYearByQuarterPlot(data, imgspec, startYear):
    # data is a DictOfCounts
    quarters = data.keys()
    quarters.sort()
    years = set()
    for q in quarters:
        years |= set(data.get(q).keys())
    years = list(years)
    years.sort()
    colours = SPECTRUM * 5
    ycs = {}
    for i in range(len(years)):
        ycs[years[i]] = colours[i]
    (img, draw, xlo, xhi, ylo, yhi) = newImage(imgspec.width, imgspec.height)
    for i in range(len(quarters)):
        x1 = xlo + (i * (xhi - xlo) / len(quarters))
        x2 = xlo + ((i+1) * (xhi-xlo) / len(quarters))
        q = quarters[i]
        subdata = [ (y, data.getCount(q, y)) for y in years if data.getCount(q,y) > 0 ]
        tot = 1.0 * sum([c for (y,c) in subdata])
        subdata = [(y, c/tot) for (y,c) in subdata]
        yt = 1.0
        for (y, c) in subdata:
            y1 = ylo + (yt * (yhi - ylo))
            yt = yt - c
            y2 = ylo + (yt * (yhi - ylo))
            draw.rectangle([x1, y1, x2, y2], outline=BLACK, fill=ycs[y])
            if y1 - y2 >= 20:
                if y == startYear:
                    y = "..%02d" % (y % 100)
                else:
                    y = "%02d" % (y % 100)
                draw.text((x1+5, (y1+y2)/2-5), str(y), fill=BLACK)
        draw.text((x1+5, yhi+10), str(q), fill=BLACK)
    del draw
    return img

def ratingToCoord(lo, hi, rating):
    return int(lo + (hi - lo) * rating / 10.0)

def plotCategoryRatings(context, cattype, category):
    import mydb, library
    if cattype == "All":
        table = ""
        clause = ""
        params = []
        category = "All"
    elif cattype == "category":
        table = "gameCategories,"
        clause = "category = %s and bggid = gameId and"
        params = [category]
    elif cattype == "mechanic":
        table = "gameMechanics,"
        clause = "mechanic = %s and bggid = gameId and"
        params = [category]
    elif cattype == "designer":
        table = "gameDesigners, "
        clause = "designerId = %s and bggid = gameId and"
        params = [int(category)]
    elif cattype == "publisher":
        table = "gamePublishers, "
        clause = "publisherId = %s and bggid = gameId and"
        params = [int(category)]
    sql = "select average, rating from games, %s geekgames where %s bggid = game and geek = %s and rating > 0" % (table, clause, "%s")
    data = mydb.query(sql, params + [context.geek])
    games = []
    for (avg, rating) in data:
        t = Thing()
        t.average = avg
        t.rating = rating
        games.append(t)
    (img, draw, xlo, xhi, ylo, yhi) = newImage(250, 250)
    draw.line([(xlo, yhi), (xhi, ylo)], GREEN, 1)
    bf = library.BestFit()
    for gg in games:
        bf.plot(gg.average, gg.rating)
        xr = ratingToCoord(xlo, xhi, gg.average)
        yr = ratingToCoord(yhi, ylo, gg.rating)
        draw.ellipse([(xr-2, yr-2), (xr+2, yr+2)], outline=BLACK, fill=BLACK)
    if bf.valid():
        (a, b) = bf.line()
        y0 = a
        y10 = a + b * 10.0
        draw.line([(ratingToCoord(xlo, xhi, 0), ratingToCoord(yhi, ylo, y0)), (ratingToCoord(xlo, xhi, 10), ratingToCoord(yhi, ylo, y10))], CYAN, 1)
    draw.text((25, 0), 'User (Y) vs BGG (X) Rating', fill=BLACK)
    del draw
    return img

def processPieData(data, colours):
    ls = []
    vs = []
    cs = []
    for (v, k) in data:
        vs.append(int(v))
        ls.append(str(int(k)))
        cs.append(colours[int(k-1)])
    return (vs, cs, ls)

def createMorgansPieCharts(data):
    [data1, data2, data3, data4] = data
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (1000, 250), WHITE)
    draw = ImageDraw.Draw(img)
    (values, colours, labels) = processPieData(data1, ALDIES_COLOURS)
    drawPie(draw, 10, 10, values, colours, labels, "Your ratings of games you own")
    (values, colours, labels) = processPieData(data2, ALDIES_COLOURS)
    drawPie(draw, 260, 10, values, colours, labels, "BGG averages of games you own")
    (values, colours, labels) = processPieData(data3, ALDIES_COLOURS)
    drawPie(draw, 510, 10, values, colours, labels, "Your ratings of all games you've ever played")
    (values, colours, labels) = processPieData(data4, ALDIES_COLOURS)
    drawPie(draw, 760, 10, values, colours, labels, "Your ratings of all games you've played in the last year")
    del draw
    return img

def createMorePieCharts(data):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (600, 600), WHITE)
    values = data.items()[:]
    total = sum([x[1] for x in values])
    tooSmall = total / 270.0
    values.sort(lambda v1, v2: -cmp(v1[1], v2[1]))
    ci = 0
    triplets = []
    remainder = total
    for (name, value) in values:
        if value < tooSmall:
            break
        triplets.append((name, value, MIKE_HULSEBUS_COLOURS[ci]))
        ci += 1
        if ci == len(MIKE_HULSEBUS_COLOURS):
            ci = 0
        remainder = remainder - value
    if remainder > 0:
        triplets.append(("Other", remainder, "#888888"))
    draw = ImageDraw.Draw(img)
    drawPieTriplets(draw, 50, 50, 500, triplets)
    del draw
    return img

def __toAngle(v):
    v = v * 360.0 - 180.0
    if v < 0:
        v += 360.0
    return int(v)

def drawPieTriplets(draw, x, y, size, triplets):
    import math
    tot = sum([v[1] for v in triplets]) * 1.0
    if tot == 0.0:
        return
    triplets = [(name, value * 1.0 / tot, colour) for (name, value, colour) in triplets]
    tot = 0.0
    xy = x, y, x + size, y + size
    for (name, value, colour) in triplets:
        draw.pieslice(xy, __toAngle(tot), __toAngle(tot + value), fill=colour)
        tot = tot + value
    draw.pieslice(xy, __toAngle(tot), __toAngle(1.0), fill=triplets[-1][2])
    tot = 0.0
    # radius of the centre of the text
    radius = size / 2.0 * 0.7
    for (name, value, colour) in triplets:
        if value * 360.0 >= 3.0:
            try:
                (sw, sh) = draw.textsize(name)
            except UnicodeEncodeError:
                name = "".join([ c for c in name if ord(c) < 128 ])
                (sw, sh) = draw.textsize(name)
            halfAngle = tot + value / 2.0
            cx = x + size / 2 + radius * math.cos((halfAngle * 6.283) - math.pi)
            cy = y + size / 2 + radius * math.sin((halfAngle * 6.283) - math.pi)
            draw.text((cx-sw/2, cy-sh/2), name, fill=BLACK)
        tot += value

def drawPie(draw, x, y, values, colours, labels, title):
    import math
    tot = sum(values) * 1.0
    if tot == 0.0:
        return
    values = [v * 1.0 / tot for v in values]
    tot = 0.0
    xy = x, y, x + PIE_SIZE, y + PIE_SIZE
    for i in range(len(values)):
        draw.pieslice(xy, int(tot * 360.0), int((tot + values[i]) * 360.0), fill=colours[i])
        tot += values[i]
    tot = 0.0
    radius = PIE_SIZE / 2.0 * 0.667
    for i in range(len(values)):
        if values[i] * 360.0 >= 20.0:
            (sw, sh) = draw.textsize(labels[i])
            halfAngle = tot + values[i] / 2.0
            cx = x + PIE_SIZE / 2 + radius * math.cos(halfAngle * 6.283)
            cy = y + PIE_SIZE / 2 + radius * math.sin(halfAngle * 6.283)
            draw.text((cx-sw/2, cy-sh/2), labels[i], fill=BLACK)
        tot += values[i]
    words = title.split(' ')
    yh = y + PIE_SIZE + 10
    while len(words) > 0:
        thisLine = words[0]
        words = words[1:]
        while len(words) > 0 and draw.textsize(thisLine + " " +words[0])[0] <= PIE_SIZE:
            thisLine = thisLine + " " + words[0]
            words = words[1:]
        draw.text((x, yh), thisLine, fill=BLACK)
        yh += 15
    
