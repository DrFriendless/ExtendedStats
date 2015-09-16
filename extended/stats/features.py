"""A feature is an encapsulation of a table / image / something that can be presented by itself on a page."""

class Feature(object):
    def __init__(self, name, htmlFile, tag, title, contentsFile=None, cssClass="ThisPage"):
        self.name = name
        self.htmlFile = htmlFile
        self.tag = tag
        self.title = title
        self.contentsFile = contentsFile
        self.cssClass = cssClass
        
    def enabled(self, options):
        return options.__dict__.get("include" + self.name)
        
class PogoTable(Feature):
    def __init__(self, selector):
        Feature.__init__(self, "PogoTable", "stats/pogotable.html", "pogotable", "Plays of Games Owned Table")
        if type(selector) == type(""):
            import selectors
            selector = selectors.getSelectorFromString(selector)
        self.selector = selector
        
    def generate(self, context):
        import generate
        (pogo, pogoCollections) = generate.getPogoData(context, self.selector)
        return { "pogo" : pogo }

class Morgan(Feature):
    def __init__(self):
        Feature.__init__(self, "Morgan", "stats/morgan.html", "mmmpie", "Pie Charts for Morgan")
        
    def generate(self, context):
        return {}

class Florence(Feature):
    def __init__(self):
        Feature.__init__(self, "Florence", "stats/florence.html", "florence", "Florence Nightingale Gamer Characterisation")
        
    def generate(self, context):
        import imggen
        florence = imggen.getFlorenceSettings()
        florenceDefault = "lastyear"   
        return { "florence" : florence, "florenceDefault" : florenceDefault }
        
class MorePie(Feature):
    def __init__(self):
        Feature.__init__(self, "More Pie Charts", "stats/morepie.html", "morepie", "Mike Hulsebus-style Pie Chart")
        
    def generate(self, context):
        morePieDefault = "lastyear"   
        return { "morePieDefault" : morePieDefault }
        
class PlaysByPublishedYear(Feature):
    def __init__(self, upsideDown):
        if upsideDown:
            Feature.__init__(self, "Pbpyu", "stats/pbpy.html", "pbpyu", "Plays of Games Owned by Published Year Upside Down")
        else:
            Feature.__init__(self, "Pbpy", "stats/pbpy.html", "pbpy", "Plays of Games Owned by Published Year")
        self.upsideDown = upsideDown
    
    def generate(self, context):
        import imgviews
        (img, rbpymap) = imgviews.playsByPublishedYear(context, self.upsideDown)
        return {"pbpydata" : imageBinaryData(img), "pbpymap" : rbpymap }
        
class OwnedByPublishedYear(Feature):
    def __init__(self, upsideDown):
        if upsideDown:
            Feature.__init__(self, "Obpyu", "stats/obpy.html", "obpyu", "Games Owned by Published Year Upside Down")
        else:
            Feature.__init__(self, "Obpy", "stats/obpy.html", "obpy", "Games Owned by Published Year")
        self.upsideDown = upsideDown
        
    def generate(self, context):
        import imgviews
        (img, obpymap) = imgviews.ownedByPublishedYear(context, self.upsideDown)
        return { "obpydata" : imageBinaryData(img), "obpymap" : obpymap }
        
class RatingByPublishedYear(Feature):        
    def __init__(self, upsideDown):
        if upsideDown:
            Feature.__init__(self, "Rbpyu", "stats/rbpy.html", "rbpyu", "Ratings by Published Year Upside Down")
        else:
            Feature.__init__(self, "Rbpy", "stats/rbpy.html", "rbpy", "Ratings by Published Year")
        self.upsideDown = upsideDown
        
    def generate(self, context):
        import imgviews
        if self.upsideDown:
            (img, rbpymap) = imgviews.ratingByPublishedYearUpsideDown(context)
        else:
            (img, rbpymap) = imgviews.ratingByPublishedYear(context)
        if len(rbpymap) == 0:
            return None
        return { "rbpydata" : imageBinaryData(img), "rbpymap" : rbpymap }

class MostUnplayed(Feature):
    def __init__(self):
        Feature.__init__(self, "MostUnplayed", "stats/mostunplayed.html", "mostunplayed", "Most Played Games That You Haven't Played")
        
    def generate(self, context):
        import generate
        mostUnplayed = generate.getMostPlayedUnplayedGames(context)
        return { "mostUnplayed" : mostUnplayed }

def imageBinaryData(img):
    import StringIO, urllib
    src = StringIO.StringIO()
    img.save(src, "PNG")
    data = urllib.quote(src.getvalue()) 
    return data
        
class PlayRate(Feature):        
    def __init__(self, selector):
        Feature.__init__(self, "PlayRate", "stats/playrate.html", "playrate", "Plays by Rating")
        self.selector = selector
        
    def generate(self, context):
        import imggen, generate
        data = generate.getPlayRateData(context, self.selector)
        if len(data[0]) == 0:
            return None
        (img, imap) = imggen.createPlayRateGraph(context, data)        
        return {"prdata" : imageBinaryData(img), "prmap" : imap }

class PlayRateOwn(Feature):        
    def __init__(self):
        import selectors
        Feature.__init__(self, "PlayRateOwn", "stats/playrateown.html", "playrateown", "Plays by Rating for Games that You Own")
        self.selector = selectors.getSelectorFromString("/owned/books/minus")
        
    def generate(self, context):
        import imggen, generate    
        data = generate.getPlayRateData(context, self.selector)
        if len(data[0]) == 0:
            return None        
        (img, imap) = imggen.createPlayRateGraph(context, data)        
        return { "prodata" : imageBinaryData(img), "promap" : imap }

class PlayRatePrevOwn(Feature):        
    def __init__(self):
        Feature.__init__(self, "PlayRatePrev", "stats/playrateprev.html", "playrateprev", "Plays by Rating for Games that You Previously Owned")
        self.selector = selectors.getSelectorFromString("/prevowned/owned/minus/books/minus")
        
    def generate(self, context):
        import imggen, generate  
        data = generate.getPlayRateData(context, self.selector)
        if len(data[0]) == 0:
            return None  
        (img, imap) = imggen.createPlayRateGraph(context, data)         
        return { "prevdata" : imageBinaryData(img), "prevmap" : imap }
        
class PlaysByMonthEver(Feature):
    def __init__(self):
        Feature.__init__(self, "PlaysByMonthEver", "stats/pbmever.html", "pbmever", "Plays by Month (Ever)")
        
    def generate(self, context):    
        import generate
        pbm = generate.getPBMData(context)
        return { "pbm" : pbm }       

class PlaysByMonthYTD(Feature):
    def __init__(self):
        Feature.__init__(self, "PlaysByMonthYTD", "stats/pbmytd.html", "pbmytd", "Plays by Month (Year to Date)")    

    def generate(self, context):        
        import generate
        pbm = generate.getPBMData(context)
        return { "pbm" : pbm }     
        
class PlaysByMonthTimeline(Feature):
    def __init__(self):  
        Feature.__init__(self, "PlaysByMonthTimeline", "stats/pbmtimeline.html", "timeline", "Plays by Month Timeline")  

    def generate(self, context):        
        import generate
        pbm = generate.getPBMData(context)
        timelineHeight = context.options.pbm.timelineHeight
        timelineWidth = context.options.pbm.timelineWidth           
        return { "pbm" : pbm, "timelineHeight" : timelineHeight, "timelineWidth" : timelineWidth }     

class PlaysByMonthGraph(Feature):
    def __init__(self):
        Feature.__init__(self, "PlaysByMonthGraph", "stats/pbmgraph.html", "pbmgraph", "Plays by Month Graph")    

    def generate(self, context):        
        import generate
        pbm = generate.getPBMData(context)
        return { "pbm" : pbm }     
        
class PlayRatings(Feature):
    def __init__(self):
        Feature.__init__(self, "PlayRatings", "stats/ratedplays.html", "pr", "Play Ratings")
        
    def generate(self, context):
        import generate
        playRatings = generate.getPlayRatings(context)
        return { "playRatings" : playRatings } 
        
class GenericTable(Feature):
    def __init__(self, selector):
        Feature.__init__(self, "GenericTable", "stats/genericgamestable.html", "generic", "Games")
        self.selector = selector
        
    def generate(self, context):
        import generate, selectors
        games = generate.getGeekGames(context, self.selector)     
        ss = selectors.getSelectorData(context)
        return { "games" : games, "selectors" : ss }
        
class Favourites(GenericTable):
    def __init__(self, selector):
        Feature.__init__(self, "Favourites", "stats/favourites.html", "favourites", "Your Favourite Games")
        self.selector = selector
        
    def generate(self, context):
        import generate
        all = GenericTable.generate(self, context)
        favourites = all["games"]
        del(all["games"])
        bggCorrelation = generate.calcCorrelation(favourites)
        bggCorrelationRankedOnly = generate.calcCorrelationRankedOnly(favourites)
        hindex = generate.calcHIndex(favourites)        
        all.update({ "favourites" : favourites, "hindex" : hindex, "bggCorrelation" : bggCorrelation, "bggCorrelationRankedOnly" : bggCorrelationRankedOnly })
        return all
        
class Pogo(Feature):
    def __init__(self, selector):
        Feature.__init__(self, "Pogo", "stats/pogo.html", "pogo", "Plays of Games")
        if type(selector) == type(""):
            import selectors
            selector = selectors.getSelectorFromString(selector)
        self.selector = selector
        
    def generate(self, context):
        import generate, imggen
        (pogo, pogoCollections) = generate.getPogoData(context, self.selector)
        pogoImgData = generate.getPogoData(context, self.selector)[0]
        (img, pogomap) = imggen.createPogoHistogram(context, pogoImgData)
        ss = selectors.getSelectorData(context)
        title = self.selector.name
        return { "collection" : pogoCollections[0], "pogomap" : pogomap, "selectors" : ss, "title" : title,
                 "url" : "/dynamic/image/pogo", "username" : context.geek }
        
class GiniTable(Feature):
    def __init__(self, selector):
        Feature.__init__(self, "Pogo", "stats/gini.html", "gini", "Gini Coefficient")
        if type(selector) == type(""):
            import selectors
            selector = selectors.getSelectorsFromString(selector)
        self.selectors = selector

    def generate(self, context):
        import generate, imggen, library
        result = []
        i = 0
        for selector in self.selectors:
            pogoData = generate.getPogoData(context, selector)[0]
            if len(pogoData) == 0:
                continue
            t = library.Thing(selector.name)
            pogoData.sort(lambda gg1, gg2: cmp(gg1.plays, gg2.plays))
            giniCoefficient, giniData = generate.produceGiniDataFromPogoDate(pogoData)
            (img, map) = imggen.createGiniGraph(context, giniData)
            t.data = giniData
            t.img = imageBinaryData(img)
            t.map = map
            t.id = "ginirow%d" % i
            i += 1
            t.coefficient = giniCoefficient
            result.append(t)
        if len(result) == 0:
            return None
        return { "giniData" : result }

class FavesByPublishedYear(Feature):
    def __init__(self):
        Feature.__init__(self, "FaveByPubYear", "stats/fgbpy.html", "fgbpy", "Your Favourite Games By Published Year")
        
    def generate(self, context):
        import generate
        fgbpy = generate.getFavouriteGamesByPublishedYear(context) 
        if len(fgbpy) == 0:
            return None
        return { "fgbpy" : fgbpy }    
        
class BestDays(Feature):
    def __init__(self):
        Feature.__init__(self, "BestDays", "stats/bestdays.html", "bestdays", "Best Days in Gaming")
        
    def generate(self, context):
        import generate
        bestDays = generate.getBestDays(context)[:20]
        if len(bestDays) == 0:
            return None
        return { "bestDays" : bestDays }          
        
class Streaks(Feature):
    def __init__(self):
        Feature.__init__(self, "Streaks", "stats/streaks.html", "streaks", "Most Consecutive Days Playing Games")
        
    def generate(self, context):
        import generate
        streaks = generate.getStreaks(context)
        if len(streaks) == 0:
            return None
        return { "streaks" : streaks }          
        
class RatingByRanking(Feature):
    def __init__(self):
        Feature.__init__(self, "RatingByRanking", "stats/ratingbyranking.html", "ratingByRanking", "Ratings by Ranking")
        
    def generate(self, context):
        import generate
        ratingByRanking = generate.getRatingByRanking(context)
        return { "ratingByRanking" : ratingByRanking }       
     
class PlaysByRanking(Feature):
    def __init__(self):
        Feature.__init__(self, "PlaysByRanking", "stats/playsByRanking.html", "playsByRanking", "Plays by Ranking")
        
    def generate(self, context):
        import generate
        playsByRanking = generate.getPlaysByRanking(context)
        return { "playsByRanking" : playsByRanking }       
     
class LeastWanted(Feature):
    def __init__(self):
        Feature.__init__(self, "LeastWanted", "stats/least.html", "least", "Why Do You Even Own These Games?")
        
    def generate(self, context):
        import generate
        least = generate.getLeastWanted(context)
        if len(least) == 0:
            return None
        return { "least" : least }    
        
class Unusual(Feature):
    def __init__(self):
        Feature.__init__(self, "Unusual", "stats/unusual.html", "unusual", "The Most Unusual Games You Own")
        
    def generate(self, context):
        import generate
        unusual = generate.getUnusualData(context)
        unusual = unusual[:10]
        if len(unusual) == 0:
            return None
        return { "unusual" : unusual }    
        
class ShouldPlay(Feature):
    def __init__(self):
        Feature.__init__(self, "ShouldPlay", "stats/shouldplay.html", "shouldplay", "Games You Should Play")
        
    def generate(self, context):
        import generate
        shouldPlay = generate.getShouldPlayData(context)
        if len(shouldPlay) == 0:
            return None
        return { "shouldPlay" : shouldPlay }    
        
class ShouldPlayOwn(Feature):
    def __init__(self):
        Feature.__init__(self, "ShouldPlayOwn", "stats/shouldplayown.html", "shouldplayown", "Games You Should Play Which You Own")
        
    def generate(self, context):
        import generate
        shouldPlayOwn = generate.getShouldPlayOwnData(context) 
        if len(shouldPlayOwn) == 0:
            return None
        return { "shouldPlayOwn" : shouldPlayOwn }    
        
class YearlySummaries(Feature):
    def __init__(self):
        Feature.__init__(self, "YearlySummaries", "stats/yearlysummaries.html", "yearly", "Yearly Summaries", cssClass="OtherPage", contentsFile="stats/yearlysummaries.html")
        
    def generate(self, context):
        import generate
        playsYears = generate.getPlaysRecordedYears(context)
        playsYearsRows = []
        PLAY_YEAR_WIDTH = 7
        while len(playsYears) > PLAY_YEAR_WIDTH:
            playsYearsRows.append(playsYears[:PLAY_YEAR_WIDTH])
            playsYears = playsYears[PLAY_YEAR_WIDTH:]
        if len(playsYears) > 0:
            playsYearsRows.append(playsYears)
        return { "playsYearsRows" : playsYearsRows }
        
class PlaysByQuarter(Feature):
    def __init__(self):
        Feature.__init__(self, "PlaysByQuarter", "stats/pbq.html", "pbq", "How Much Do You Play New Games?")
        
    def generate(self, context):
        import generate
        # decide whether to show the image or not
        if not generate.hasPlaysData(context):
            return None
        return {}      
        
class TemporalHotnessMonth(Feature):   
    def __init__(self):
        Feature.__init__(self, "TempHot", "stats/temphotmonth.html", "thm", "Temporal Hotness by Month")    
        
    def generate(self, context):
        import generate
        if not generate.hasPlaysData(context):
            return None       
        data = generate.getTemporalHotnessMonthData(context)
        return { "thm" : data }
        
class TemporalHotnessDate(Feature):   
    def __init__(self):
        Feature.__init__(self, "TempHotDate", "stats/temphotdate.html", "thd", "Temporal Hotness by Date")    
        
    def generate(self, context):
        import generate
        if not generate.hasPlaysData(context):
            return None       
        data = generate.getTemporalHotnessDateData(context)
        return { "thd" : data }
        
class TemporalHotnessDay(Feature):   
    def __init__(self):
        Feature.__init__(self, "TempHotDay", "stats/temphotday.html", "thday", "Temporal Hotness by Day of Week")    
        
    def generate(self, context):
        import generate
        if not generate.hasPlaysData(context):
            return None       
        data = generate.getTemporalHotnessDayData(context)
        return { "thday" : data }
        
class DimesByDesigner(Feature):
    def __init__(self):
        Feature.__init__(self, "DByD", "stats/dimesbydesigner.html", "dimesbydesigner", "Dimes by Designer")
        self.resultFile = "stats/dimesbydesigner_result.html"
        
    def generate(self, context):
        import generate
        designerDimes = generate.getDimesByDesigner(context)
        if len(designerDimes) == 0:
            return None
        return { "designerDimes" : designerDimes }
    
class FeatureList(Feature):
    def __init__(self):
        Feature.__init__(self, "flist", "stats/featurelist.html", "featurelist", "Feature List")
        
    def generate(self, context):
        return { "features" : FEATURES }
    
class Consistency(Feature):
    DEFAULT_SELECTOR = "/played"
    
    def __init__(self, selector, months):
        Feature.__init__(self, "consistency", "stats/consistency.html", "consistency", "Consistency of Play Graph")
        if type(selector) == type(""):
            import selectors
            selector = selectors.getSelectorFromString(selector)
        self.selector = selector
        self.months = months
        
    def generate(self, context):
        import generate
        data = generate.getConsistencyData(context, self.selector, self.months)
        if len(data) == 0:
            return None
        return { "consistencyData" : data }


class PlaysByYear(Feature):
    def __init__(self):
        Feature.__init__(self, "PlaysByYear", "stats/pby.html", "pby", "Plays By Year")

    def generate(self, context):
        import generate
        data = generate.getPlaysByYearData(context)
        if len(data) == 0:
            return None
        return { "pbyData" : data }
        
class PlayLocations(Feature):
    def __init__(self):
        Feature.__init__(self, "PlayLocations", "stats/locations.html", "locations", "Play Locations")

    def generate(self, context):
        import generate
        data = generate.getPlayLocationsData(context)
        if len(data) == 0:
            return None
        return { "locations" : data }

class FirstPlaysVsRating(Feature):
    def __init__(self):
        Feature.__init__(self, "FirstPlayVsRating", "stats/fpvr.html", "fpvr", "First Plays vs Rating")

    def generate(self, context):
        return {  }

import selectors, views
FEATURES = [ Pogo(views.POGO_SELECTOR), PogoTable(views.POGO_SELECTOR), Morgan(), Florence(), MorePie(),
             PlaysByPublishedYear(False), PlaysByPublishedYear(True),
             OwnedByPublishedYear(False), OwnedByPublishedYear(True),
             RatingByPublishedYear(False), RatingByPublishedYear(True), MostUnplayed(),
             GenericTable(selectors.OwnedGamesSelector()),
             PlayRate(selectors.PlayedGamesSelector()), PlayRateOwn(), PlayRatePrevOwn(),
             PlaysByMonthEver(), PlaysByMonthYTD(), PlaysByMonthGraph(), PlayRatings(),
             Favourites(selectors.AllGamesSelector()),
             FavesByPublishedYear(), BestDays(), Streaks(), RatingByRanking(), PlaysByRanking(), LeastWanted(),
             Unusual(), ShouldPlay(), FirstPlaysVsRating(),
             ShouldPlayOwn(), YearlySummaries(), PlaysByQuarter(), TemporalHotnessMonth(), TemporalHotnessDate(),
             TemporalHotnessDay(), PlaysByMonthTimeline(), DimesByDesigner(),
             Consistency(Consistency.DEFAULT_SELECTOR, 96), PlaysByYear(), PlayLocations(),
             GiniTable(views.POGO_SELECTOR)]

FEATURES_BY_KEY = {}
for f in FEATURES:
    FEATURES_BY_KEY[f.tag] = f
