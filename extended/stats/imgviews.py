from django.http import HttpResponse

class ImageSpecs(object):
    def __init__(self, request):
        self.width = 800
        self.height = 600
        if request.COOKIES.get("width") is not None:
            try:
                self.width = int(request.COOKIES["width"])
            except:
                pass
        if request.COOKIES.get("height") is not None:
            try:
                self.height = int(request.COOKIES["height"])
            except:
                pass

def pogo(request, param):
    import library, views, imggen, generate
    try:
        (username, selector) = library.checkGeekGetSelector(param, request, views.POGO_SELECTOR[1:])
        options = views.Options(request)
        ispec = ImageSpecs(request)
        context = views.OptimisationContext(username, options, ispec)  
        data = generate.getPogoData(context, selector)[0]
        (img, imap) = imggen.createPogoHistogram(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def getImage(*args, **kwargs):
    import StringIO, urllib2, Image
    f = StringIO.StringIO(urllib2.urlopen(*args, **kwargs).read())   
    return Image.open(f)

def pbmGraph(request, param):
    import library, views, imggen, generate
    try:
        context = views.interpretRequest(request, param)
        data = generate.getPBMData(context)
        img = imggen.createPBMGraph(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def newPlays(request, param):
    import views, library, generate, imggen
    try:
        context = views.interpretRequest(request, param)     
        data = generate.getNewPlaysData(context)
        img = imggen.createNewPlaysGraph(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def lifetime(request, param):
    import views, library, generate, imggen
    try:
        context = views.interpretRequest(request, param)     
        data = generate.getLifetimeData(context)
        img = imggen.createLifetimeGraph(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def lifetimeByRating(request, param):
    import views, library, generate, imggen
    try:
        context = views.interpretRequest(request, param)     
        data = generate.getLifetimeByRatingData(context)
        img = imggen.createLifetimeByRatingGraph(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def lagHistogram(request, param):
    import views, library, generate, imggen
    try:
        context = views.interpretRequest(request, param)        
        data = generate.getLagData(context)
        img = imggen.createLagHistogram(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png")

def mostPlayedCumulativeTimeline(request, param):
    import library, views, imggen, generate
    try:
        context = views.interpretRequest(request, param)
        data = generate.getMostPlayedTimelineData(context)
        img = imggen.createMostPlayedTimelineGraph(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")
        return HttpResponse(img, mimetype="image/png")
        
def firstPlayVsRating(request, param):        
    import views, library, generate, imggen
    try:
        context = views.interpretRequest(request, param)  
        data = generate.getFirstPlayVsRatingData(context.geek)
        years = generate.getGeekYears(context.geek)
        img = imggen.createFirstPlayVsRatingGraph(context, data, years)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def playsByPublishedYear(context, upsideDown):
    import generate, imggen
    data = generate.getPlaysByPublishedYearData(context)
    return imggen.createPlaysByPublishedYearGraph(context, data, upsideDown)

def ratingByPublishedYear(context):
    import generate, imggen
    data = generate.getRatingByPublishedYearData(context)
    return imggen.createRatingByPublishedYearGraph(context, data, False)

def ratingByPublishedYearUpsideDown(context):
    import generate, imggen
    data = generate.getRatingByPublishedYearData(context)
    return imggen.createRatingByPublishedYearGraph(context, data, True)

def ownedByPublishedYear(context, upsideDown):
    import generate, imggen
    data = generate.getOwnedByPublishedYearData(context)
    return imggen.createOwnedByPublishedYearGraph(context, data, upsideDown)

def playrate(request, param):
    import views, library, generate, imggen
    try:
        if "/" in param:
            fields = param.split("/")
            selector = "/".join(fields[1:])
            context = views.interpretRequest(request, fields[0])
        else:
            selector = "all"
            context = views.interpretRequest(request, param)  
        import selectors
        data = generate.getPlayRateData(context, selector)
        (img, imap) = imggen.createPlayRateGraph(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def playrateown(request, param):    
    import views, library, generate, imggen
    try:
        context = views.interpretRequest(request, param)
        import selectors
        data = generate.getPlayRateData(context, "owned")
        (img, imap) = imggen.createPlayRateGraph(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def playrateprevown(request, param):    
    import views, library, generate, imggen
    try:
        context = views.interpretRequest(request, param)
        import selectors
        data = generate.getPlayRateData(context, "prevowned")
        (img, imap) = imggen.createPlayRateGraph(context, data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def playsByQuarter(request, param):    
    import views, library, generate, imggen
    try:
        context = views.interpretRequest(request, param)
        data = generate.getPlaysByQuarterData(context, 1990)
        img = imggen.createPlaysForYearByQuarterPlot(data, context.imageSpec, 1990)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png")    
        
def morgansPieCharts(request, param):
    import views, library, generate, imggen
    try:
        context = views.interpretRequest(request, param)
        data = generate.getMorgansPieChartsData(context.geek)
        img = imggen.createMorgansPieCharts(data)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png")     
        
def morePieCharts(request, param):  
    import library, imggen, generate, views
    try:
        fields = param.split("/")
        if len(fields) > 0:
            context = views.interpretRequest(request, fields[0])
            (plays, messages, year, month, day, args) = context.substrate.getPlaysForDescribedRange(fields[1:])
            data = generate.morePieChartData(plays)
            img = imggen.createMorePieCharts(data)
            return library.imageResponse(img)
        else:
            img = open("error.png")
            return HttpResponse(img, mimetype="image/png")
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png")     
        
def category(request, param):
    import library, views, imggen
    try:
        fields = param.split("/")
        context = views.interpretRequest(request, fields[0])  
        cattype = fields[1]
        cat = "/".join(fields[2:])
        img = imggen.plotCategoryRatings(context, cattype, cat)
        return library.imageResponse(img)
    except library.NoSuchGeekException:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png")                 
