from django.http import HttpResponse
from models import Geeks
import dynlib, views, imggen, generate

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
    try:
        (username, geek, selector) = dynlib.checkGeekGetSelector(param, request, views.POGO_SELECTOR[1:])
        options = views.Options(request)
        ispec = ImageSpecs(request)
        context = views.OptimisationContext(username, options, ispec)  
        data = generate.getPogoData(context, selector)[0]
        (img, imap) = imggen.createPogoHistogram(context, data)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def getImage(*args, **kwargs):
    import StringIO, urllib2, Image
    f = StringIO.StringIO(urllib2.urlopen(*args, **kwargs).read())   
    return Image.open(f)

def pbmGraph(request, param):
    try:
        context = views.interpretRequest(request, param)
        data = generate.getPBMData(context)
        img = imggen.createPBMGraph(context, data)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def newPlays(request, param):
    import views
    try:
        context = views.interpretRequest(request, param)     
        data = generate.getNewPlaysData(context)
        img = imggen.createNewPlaysGraph(context, data)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def lifetime(request, param):
    import views
    try:
        context = views.interpretRequest(request, param)     
        data = generate.getLifetimeData(context)
        img = imggen.createLifetimeGraph(context, data)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def lifetimeByRating(request, param):
    import views
    try:
        context = views.interpretRequest(request, param)     
        data = generate.getLifetimeByRatingData(context)
        img = imggen.createLifetimeByRatingGraph(context, data)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def lagHistogram(request, param):
    import views
    try:
        context = views.interpretRequest(request, param)        
        data = generate.getLagData(context)
        img = imggen.createLagHistogram(context, data)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def firstPlayVsRating(request, param):        
    try:
        context = views.interpretRequest(request, param)  
        data = generate.getFirstPlayVsRatingData(context.geek)
        years = generate.getGeekYears(context.geek)
        img = imggen.createFirstPlayVsRatingGraph(context, data, years)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def playsByPublishedYear(context):        
    data = generate.getPlaysByPublishedYearData(context)
    (img, imap) = imggen.createPlaysByPublishedYearGraph(context, data)
    return (img, imap)
        
def ratingByPublishedYear(context):        
    data = generate.getRatingByPublishedYearData(context)
    (img, imap) = imggen.createRatingByPublishedYearGraph(context, data)
    return (img, imap)
        
def ownedByPublishedYear(context):        
    data = generate.getOwnedByPublishedYearData(context)
    (img, imap) = imggen.createOwnedByPublishedYearGraph(context, data)
    return (img, imap)
        
def playrate(request, param):    
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
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def playrateown(request, param):    
    try:
        context = views.interpretRequest(request, param)
        import selectors
        data = generate.getPlayRateData(context, "owned")
        (img, imap) = imggen.createPlayRateGraph(context, data)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def playrateprevown(request, param):    
    try:
        context = views.interpretRequest(request, param)
        import selectors
        data = generate.getPlayRateData(context, "prevowned")
        (img, imap) = imggen.createPlayRateGraph(context, data)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png") 
        
def playsByQuarter(request, param):    
    try:
        context = views.interpretRequest(request, param)
        data = generate.getPlaysByQuarterData(context, 1990)
        img = imggen.createPlaysForYearByQuarterPlot(data, context.imageSpec, 1990)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png")    
        
def morgansPieCharts(request, param):    
    try:
        context = views.interpretRequest(request, param)
        data = generate.getMorgansPieChartsData(context.geek)
        img = imggen.createMorgansPieCharts(data)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png")     
        
def morePieCharts(request, param):  
    import dynlib, imggen, generate, views
    try:
        fields = param.split("/")
        if len(fields) > 0:
            context = views.interpretRequest(request, fields[0])
            (plays, messages, year, month, day, args) = context.substrate.getPlaysForDescribedRange(fields[1:])
            data = generate.morePieChartData(plays)
            img = imggen.createMorePieCharts(data)
            return dynlib.imageResponse(img)
        else:
            img = open("error.png")
            return HttpResponse(img, mimetype="image/png")
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png")     
        
def category(request, param):
    try:
        fields = param.split("/")
        context = views.interpretRequest(request, fields[0])  
        cattype = fields[1]
        cat = "/".join(fields[2:])
        img = imggen.plotCategoryRatings(context, cattype, cat)
        return dynlib.imageResponse(img)
    except Geeks.DoesNotExist:
        img = open("error.png")   
        return HttpResponse(img, mimetype="image/png")                 
