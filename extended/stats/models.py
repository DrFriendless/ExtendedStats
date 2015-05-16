# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class SimpleManager(models.Manager):        
    def query(self, sql, args=[]):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(sql, args)
        result = cursor.fetchall()
        cursor.close()   
        return result       

class NoPrimaryKeyManager(SimpleManager):
    def filter(self, cols=None, **kwargs):
        from django.db import connection
        extraClauses = []
        extraArgs = []
        for (k, v) in kwargs.items():
            if type(v) == type(()):
                del kwargs[k]
                (s, e) = v
                if s is not None and e is not None:
                    extraClauses.append("%s between %s and %s" % (k, "%s", "%s"))
                    extraArgs = extraArgs + [s, e]
                elif s is not None:
                    extraClauses.append("%s >= %s" % (k, "%s"))
                    extraArgs.append(s)
                elif e is not None:
                    extraClauses.append("%s < %s" % (k, "%s"))
                    extraArgs.append(e) 
            elif type(v) == type([]):
                del kwargs[k]
                if len(v) > 1:
                    extraClauses.append("%s in %s" % (k, "%s"))
                    extraArgs.append(v)               
                else:
                    extraClauses.append("%s = %s" % (k, "%s"))
                    extraArgs.append(v[0])
        cursor = connection.cursor()
        OMIT = [ "id" ] + kwargs.keys()
        attCols = [ f.get_attname_column() for f in self.model._meta.fields if f.get_attname() not in OMIT ]
        columns = [ f[1] for f in attCols ]
        if cols is not None:
            columns = cols
        args = extraArgs + [v for (k,v) in kwargs.items()]
        where = " and ".join(extraClauses + ["%s = %s" % (k,"%s") for (k,v) in kwargs.items()])
        header = ", ".join(columns)   
        sql = "select %s from %s where %s" % (header, self.model._meta.db_table, where)
        cursor.execute(sql, args)
        result = cursor.fetchall()
        cursor.close()   
        if len(columns) == 1:
            result = [x[0] for x in result]
        return (columns, result)          
        
    def _buildObjects(self, data):
        import library
        columns = data[0]
        rows = data[1]
        result = []
        for row in rows:
            t = library.Thing()
            for i in range(len(columns)):
                t.__dict__[columns[i]] = row[i]
            result.append(t)
        return result
        
    def getObjects(self, **kwargs):
        data = self.filter(**kwargs)
        return self._buildObjects(data)

class Designers(models.Model):
    name = models.CharField(max_length=255)
    bggid = models.IntegerField(primary_key=True)
    boring = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=255, blank=True)
    class Meta:
        db_table = u'designers'
        
    def __eq__(self, other):
        return self.bggid == other.bggid

    def __ne__(self, other):
        return self.bggid != other.bggid
        
    def __cmp__(self, other):
        return cmp(self.name, other.name)

class Files(models.Model):
    filename = models.CharField(max_length=384)
    url = models.CharField(unique=True, max_length=255, primary_key=True)
    lastupdate = models.DateTimeField(null=True, db_column='lastUpdate', blank=True)
    processmethod = models.CharField(max_length=384, db_column='processMethod')
    nextupdate = models.DateTimeField(null=True, db_column='nextUpdate', blank=True)
    geek = models.CharField(max_length=384, blank=True)
    description = models.CharField(max_length=384, blank=True)
    tillnextupdate = models.CharField(max_length=384, db_column='tillNextUpdate', blank=True)
    objects = SimpleManager()    
    class Meta:
        db_table = u'files'

class Games(models.Model):
    bggid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=768)
    average = models.FloatField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    yearpublished = models.IntegerField(null=True, db_column='yearPublished', blank=True)
    minplayers = models.IntegerField(null=True, db_column='minPlayers', blank=True)
    maxplayers = models.IntegerField(null=True, db_column='maxPlayers', blank=True)
    playtime = models.IntegerField(null=True, db_column='playTime', blank=True)
    usersrated = models.IntegerField(null=True, db_column='usersRated', blank=True)
    userstrading = models.IntegerField(null=True, db_column='usersTrading', blank=True)
    userswanting = models.IntegerField(null=True, db_column='usersWanting', blank=True)
    userswishing = models.IntegerField(null=True, db_column='usersWishing', blank=True)
    averageweight = models.FloatField(null=True, db_column='averageWeight', blank=True)
    bayesaverage = models.FloatField(null=True, db_column='bayesAverage', blank=True)
    stddev = models.FloatField(null=True, db_column='stdDev', blank=True)
    median = models.FloatField(null=True, blank=True)
    numcomments = models.IntegerField(null=True, db_column='numComments', blank=True)
    expansion = models.IntegerField()
    thumbnail = models.CharField(max_length=768, blank=True)
    usersowned = models.IntegerField(null=True, db_column='usersOwned', blank=True)
    subdomain = models.CharField(max_length=45, blank=True)
    
    class Meta:
        db_table = u'games'
        ordering = ["name"]
        
    def __eq__(self, other):
        if other is None:
            return False
        return self.bggid == other.bggid
        
    def __hash__(self):
        return self.bggid
        
    def __repr__(self):
        return self.name

class Geeks(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    shouldplay = models.IntegerField()
    avatar = models.CharField(max_length=768, blank=True)
    class Meta:
        db_table = u'geeks'
        ordering = ["username"]
        
    def __repr__(self):
        return self.username

class GeekGames(models.Model):
    geek = models.ForeignKey(Geeks, db_column='geek')
    game = models.ForeignKey(Games, db_column='game')
    rating = models.FloatField()
    owned = models.IntegerField(null=True, blank=True)
    prevowned = models.IntegerField(null=True, blank=True)
    wanttobuy = models.IntegerField(null=True, blank=True)
    wanttoplay = models.IntegerField(null=True, blank=True)
    preordered = models.IntegerField(null=True, blank=True)
    want = models.IntegerField(null=True, blank=True)
    wish = models.IntegerField(null=True, blank=True)
    trade = models.IntegerField(null=True, blank=True)
    comment = models.CharField(max_length=3072, blank=True)
    # this can be null for a book, or for a new user who hasn't been processed yet.
    plays = models.IntegerField(null=True, blank=True)
    objects = NoPrimaryKeyManager()
    class Meta:
        db_table = u'geekgames'   
   
    def __repr__(self):
        return "%s@%s" % (`self.game`, `self.geek`)    

class GeekGameTags(models.Model):
    geek = models.ForeignKey(Geeks, db_column='geek')
    game = models.ForeignKey(Games, db_column='game')
    tag = models.CharField(max_length=384)
    class Meta:
        db_table = u'geekgametags'

def q(v):
    if type(v) == type(""):
        return "'%s'" % v
    else:
        return str(v)        
        
class History(models.Model):
    geek = models.CharField(max_length=384)
    ts = models.DateTimeField()
    friendless = models.IntegerField(null=True, blank=True)
    wanted = models.IntegerField(null=True, blank=True)
    wished = models.IntegerField(null=True, blank=True)
    owned = models.IntegerField(null=True, blank=True)
    unplayed = models.IntegerField(null=True, blank=True)
    distinctplayed = models.IntegerField(null=True, db_column='distinctPlayed', blank=True)
    traded = models.IntegerField(null=True, blank=True)
    nickelpercent = models.FloatField(db_column='nickelPercent')
    youraverage = models.FloatField(db_column='yourAverage')
    percentplayedever = models.FloatField(db_column='percentPlayedEver')
    percentplayedthisyear = models.FloatField(db_column='percentPlayedThisYear')
    averagepogo = models.FloatField(db_column='averagePogo')
    bggaverage = models.FloatField(db_column='bggAverage')
    curmudgeon = models.FloatField()
    meanyear = models.FloatField(db_column='meanYear')
    the100 = models.IntegerField(null=True, blank=True)
    sdj = models.IntegerField(null=True, blank=True)
    top50 = models.IntegerField(null=True, blank=True)
    totalplays = models.IntegerField(null=True, db_column='totalPlays', blank=True)
    medyear = models.IntegerField(null=True, db_column='medYear', blank=True)
    objects = NoPrimaryKeyManager()
    class Meta:
        db_table = u'history'
        ordering = ["ts"]

class MonthsPlayed(models.Model):
    geek = models.ForeignKey(Geeks, db_column='geek')
    month = models.IntegerField()
    year = models.IntegerField()
    class Meta:
        db_table = u'monthsplayed'

class Plays(models.Model):
    game = models.IntegerField()
    geek = models.CharField(max_length=384)
    playdate = models.DateField(db_column='playDate') # Field name made lowercase.
    quantity = models.IntegerField()
    raters = models.IntegerField()
    ratingstotal = models.IntegerField(db_column='ratingsTotal')
    basegame = models.IntegerField(null=True)
    location = models.CharField(max_length=32)    
    objects = NoPrimaryKeyManager()    
    class Meta:
        db_table = u'plays'

class Publishers(models.Model):
    name = models.CharField(max_length=762)
    bggid = models.IntegerField(primary_key=True)
    url = models.CharField(max_length=762, blank=True)
    class Meta:
        db_table = u'publishers'

class Series(models.Model):
    name = models.CharField(max_length=384)
    game = models.ForeignKey(Games, db_column='game')
    class Meta:
        db_table = u'series'

class GameCategories(models.Model):
    gameid = models.ForeignKey(Games, db_column='gameId')
    category = models.CharField(max_length=768)
    objects = NoPrimaryKeyManager()
    class Meta:
        db_table = u'gameCategories'

class GameDesigners(models.Model):
    gameid = models.ForeignKey(Games, db_column='gameId')
    designerid = models.ForeignKey(Designers, db_column='designerId')
    objects = NoPrimaryKeyManager()
    class Meta:
        db_table = u'gameDesigners'

class GameMechanics(models.Model):
    gameid = models.ForeignKey(Games, db_column='gameId')
    mechanic = models.CharField(max_length=768)
    objects = NoPrimaryKeyManager()
    class Meta:
        db_table = u'gameMechanics'

class GamePublishers(models.Model):
    gameid = models.ForeignKey(Games, db_column='gameId')
    publisherid = models.ForeignKey(Publishers, db_column='publisherId')
    objects = NoPrimaryKeyManager()
    class Meta:
        db_table = u'gamePublishers'

class Expansions(models.Model):
    basegame = models.ForeignKey(Games, db_column='basegame', related_name='expansion_basegames')
    expansion = models.ForeignKey(Games, db_column='expansion', related_name='expansion_expansions')
    class Meta:
        db_table = u'expansions'


