from django.core.context_processors import csrf
from django import forms        
from django.shortcuts import render_to_response

class CookieForm(forms.Form):
    username = forms.CharField(max_length=100,  label="BGG user name", required=False)
    width = forms.IntegerField(label = "Image width", required=False)
    height = forms.IntegerField(label = "Image height", required=False)
    rbpyUpsideDown = forms.BooleanField(label="Show Ratings By Published Year Upside Down", required=False)
    obpyUpsideDown = forms.BooleanField(label="Show Games Owned By Published Year Upside Down", required=False)
    pbpyUpsideDown = forms.BooleanField(label="Show Plays of Games Owned By Published Year Upside Down", required=False)
    pogoExpansions = forms.BooleanField(label="Plays Of Games Owned: exclude expansions", required=False)
    pogoTrades = forms.BooleanField(label="Plays Of Games Owned: exclude items up for trade", required=False)
    faveExpansions = forms.BooleanField(label="Favourites: exclude expansions", required=False)
    faveTrades = forms.BooleanField(label="Favourites: exclude items up for trade", required=False)
    timelineHeight = forms.IntegerField(label="PBM Timeline: frame height", required=False)
    timelineWidth = forms.IntegerField(label="PBM Timeline: frame width", required=False)
    playrateExpansions = forms.BooleanField(label="Plays by Rating: exclude expansions", required=False)
    playrateTrades = forms.BooleanField(label="Plays by Rating: exclude games up for trade", required=False)
    playrateUnrated = forms.BooleanField(label="Plays by Rating: exclude unrated games", required=False)
    obpyExpansions = forms.BooleanField(label="Games Owned by Published Year: exclude expansions", required=False)
    obpyTrades = forms.BooleanField(label="Games Owned by Published Year: exclude games up for trade", required=False)
    pbmExpansions = forms.BooleanField(label="Plays by Month: exclude expansions", required=False)
    pbmTrades = forms.BooleanField(label="Plays by Month: exclude games up for trade", required=False)   
    
    def __init__(self, *args, **kwargs):
        super(CookieForm, self).__init__(*args, **kwargs)
        import features
        for feature in features.FEATURES:
            label = "User Tab: include %s" % feature.title
            self.fields["user" + feature.name] = forms.BooleanField(label=label + " [%s]" % feature.tag, required=False)  

    def prepareResponse(self,  response):
        import features
        username = self.cleaned_data['username']        
        if username is not None:
            set_cookie(response,  'username', username)
        width = self.cleaned_data['width']
        if width is not None:
            set_cookie(response, 'width', width)
        height = self.cleaned_data['height']
        if height is not None:
            set_cookie(response, 'height', height)
        rbpyUpsideDown = self.cleaned_data['rbpyUpsideDown']
        if rbpyUpsideDown is not None:
            set_cookie(response, 'rbpyUpsideDown', rbpyUpsideDown)
        obpyUpsideDown = self.cleaned_data['obpyUpsideDown']
        if obpyUpsideDown is not None:
            set_cookie(response, 'obpyUpsideDown', obpyUpsideDown)
        pbpyUpsideDown = self.cleaned_data['pbpyUpsideDown']
        if pbpyUpsideDown is not None:
            set_cookie(response, 'pbpyUpsideDown', pbpyUpsideDown)
        pogoExpansions = self.cleaned_data['pogoExpansions']
        if pogoExpansions is not None:
            set_cookie(response, 'pogoExpansions', pogoExpansions)
        pogoTrades = self.cleaned_data['pogoTrades']
        if pogoTrades is not None:
            set_cookie(response, 'pogoTrades', pogoTrades)
        faveExpansions = self.cleaned_data['faveExpansions']
        if faveExpansions is not None:
            set_cookie(response, 'faveExpansions', faveExpansions)
        faveTrades = self.cleaned_data['faveTrades']
        if faveTrades is not None:
            set_cookie(response, 'faveTrades', faveTrades)
        timelineHeight = self.cleaned_data['timelineHeight']
        if timelineHeight is not None:
            set_cookie(response, 'timelineHeight', timelineHeight)
        timelineWidth = self.cleaned_data['timelineWidth']
        if timelineWidth is not None:
            set_cookie(response, 'timelineWidth', timelineWidth)
        self.setCleanedCookie("obpyExpansions", response)
        self.setCleanedCookie("obpyTrades", response)
        self.setCleanedCookie("pbmExpansions", response)
        self.setCleanedCookie("pbmTrades", response)
        self.setCleanedCookie("playrateExpansions", response)
        self.setCleanedCookie("playrateTrades", response)
        self.setCleanedCookie("playrateUnrated", response)
        for feature in features.FEATURES:
            key = feature.name
            self.setCleanedCookie("user" + key, response)
        
    def setCleanedCookie(self, name, response):
        x = self.cleaned_data[name]
        if x is not None:
            set_cookie(response, name, x)
                                  
def cookies(request):
    import views
    options = views.Options(request)    
    if request.method == 'POST': # If the form has been submitted...
        form = CookieForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            vals =  { 'form': form,  'cookies' : request.COOKIES, 'options' : options }
            vals.update(csrf(request))
            response = render_to_response('stats/cookies.html', vals)
            form.prepareResponse(response)
            return response
    else:
        form = CookieForm(request.COOKIES)
    vals =  { 'form': form,  'cookies' : request.COOKIES, 'options' : options }
    vals.update(csrf(request))
    return render_to_response('stats/cookies.html', vals)
    
def set_cookie(response, key, value, days_expire = None):    
    import datetime
    if days_expire is None:
        max_age = 365*24*60*60  #one year
    else:
        max_age = days_expire*24*60*60 
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    try:
        response.set_cookie(key, value, max_age=max_age, expires=expires, domain="friendlessstats.dtdns.net", secure=None)
    except AttributeError:
        pass
        
