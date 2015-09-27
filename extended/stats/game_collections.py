from django import forms 

class CreateCollectionForm(forms.Form):
    name = forms.CharField(max_length=128,  label="Collection Name", required=False)
    description = forms.CharField(max_length=512,  label="Collection Description", required=False)

class CreateGroupForm(forms.Form):
    name = forms.CharField(max_length=128,  label="Group Name", required=False)
    description = forms.CharField(max_length=512,  label="Group Description", required=False)    
    
class AjaxForm( forms.Form ):
    input = forms.CharField( required=True )
        
def getAllCollectionsForGeek(context, includeGames = False):
    import mydb
    sql = "select collectionname, description, collectionindex, ckey from collections where geek = %s order by 3"
    collectionData = mydb.query(sql,  [context.geek])
    ckeys = [ row[3] for row in collectionData ]
    groupData = []
    gameData = []
    if len(ckeys) > 0:
        ckeystr = "(%s)" % ",".join([str(ck) for ck in ckeys])
        sql = "select groupindex, groupname, groupdesc, display, ckey from collectiongroups where ckey in " + ckeystr + " order by 1"
        groupData = mydb.query(sql)
        if includeGames:
            sql = "select groupindex, bggid, ckey from collectiongames where ckey in " + ckeystr + " order by orderindex"
            gameData = mydb.query(sql)
    return buildCollections(context, collectionData, groupData, gameData)
    
def deleteCollection(context, index):
    import mydb
    sql = "select ckey from collections where geek = %s and collectionindex = %s"
    ckeyData = mydb.query(sql,  [context.geek, index])
    if len(ckeyData) < 0:
        return
    ckey = ckeyData[0][0]    
    mydb.update("delete from collectiongames where ckey = %d" % ckey)    
    mydb.update("delete from collectiongroups where ckey = %d" % ckey)    
    mydb.update("delete from collections where ckey = %d" % ckey)    

def getNextCollectionIndex(context):
    import mydb
    sql = "select collectionindex from collections where geek = %s"
    cindexes = mydb.query(sql,  [context.geek])
    indexes = [ c[0] for c in cindexes ]
    newIndex = 0
    while newIndex in indexes:
        newIndex = newIndex + 1   
    return newIndex
    
def makeNewCollection(context, cindex):
    import library
    newCollection = library.Thing()
    newCollection.name = "New Collection"
    newCollection.description = "What is the purpose of this collection?"
    newCollection.index = cindex
    newGroup = library.Thing()
    newGroup.name = "New Group"
    newGroup.description = "New group Description"
    newGroup.index = 0
    newGroup.display = 1
    newGroup.games = []
    newCollection.groups = [ newGroup ]    
    return newCollection 
    
def getCollectionForGeek(context, index, includeGameData = False):
    import mydb
    sql = "select collectionname, description, collectionindex, ckey from collections where geek = %s and collectionindex = %s order by 3"
    collectionData = mydb.query(sql,  [context.geek, index])
    ckey = collectionData[0][3]
    sql = "select groupindex, groupname, groupdesc, display, ckey from collectiongroups where ckey = %s order by 1"
    groupData = mydb.query(sql, [ckey])
    if includeGameData:
        sql = "select groupindex, bggid, ckey from collectiongames where ckey = %s order by orderindex"
        gameData = mydb.query(sql, [ckey])
    else:
        gameData = []
    result = buildCollections(context, collectionData, groupData, gameData)
    if len(result) > 0:
        return result[0]
    return makeNewCollection(context, index)
    
def buildCollections(context, collectionData, groupData, gameData):   
    import library 
    result = []
    byCkey = {}
    for (name, description, index, ckey) in collectionData:
        t = library.Thing()
        t.name = name
        t.description = description
        t.index = index
        t.groups = []
        t.byGroup = {}
        t.new = False
        result.append(t)
        byCkey[ckey] = t
    for (index, name, description, display, ckey) in groupData:
        t = library.Thing()
        t.name = name
        t.description = description
        t.index = index
        t.display = display
        t.games = []
        byCkey[ckey].groups.append(t)
        byCkey[ckey].byGroup[index] = t
    games = context.substrate.getGames([t[1] for t in gameData])
    for (groupindex, bggid, ckey) in gameData:
        if byCkey[ckey].byGroup.get(groupindex) is None:
            continue
        byCkey[ckey].byGroup[groupindex].games.append(games[bggid])
    for c in byCkey.values():
        total = 0
        for g in c.groups:
            g.count = len(g.games)
            total = total + g.count
        c.deleteAllowed = total == 0
    return result
    
def esc(s):
    import MySQLdb
    return MySQLdb.escape_string(s)    
    
def saveCollectionFromJson(username, index, model):
    import library, mydb
    sql = "select ckey from collections where geek = %s and collectionindex = %s"
    ckeyData = mydb.query(sql,  [username, index])
    ckey = None
    if len(ckeyData) > 0:
        ckey = ckeyData[0][0]
    collRow = library.Row()
    collRow.collectionname = esc(model["name"])
    collRow.description = esc(model["description"])
    collRow.collectionindex = index
    collRow.geek = username
    if ckey is not None:
        collRow.ckey = ckey
        mydb.saveRow(collRow, "collections", "ckey = %d" % ckey)
    else:
        mydb.saveRow(collRow, "collections", None)
        ckeyData = mydb.query(sql,  [username, index]) 
        ckey = ckeyData[0][0]
    mydb.update("delete from collectiongroups where ckey = %d" % ckey)
    for g in model["groups"]:
        groupRow = library.Row()
        groupRow.ckey = ckey
        groupRow.groupname = esc(g["name"])
        groupRow.groupindex = g["index"]
        groupRow.groupname = g["name"]
        groupRow.groupdesc = esc(g["description"])
        groupRow.display = g["display"]                             
        mydb.saveRow(groupRow, "collectiongroups", None)
    mydb.update("delete from collectiongames where ckey = %d" % ckey)  
    db = mydb.get()
    for g in model["groups"]:
        order = 0    
        for game in g["games"]:
            gameRow = library.Row()
            gameRow.groupindex = g["index"]
            gameRow.bggid = game["id"]
            gameRow.orderindex = order
            order = order + 1
            gameRow.ckey = ckey
            mydb.saveRowDb(db, gameRow, "collectiongames", None)
    db.commit()
    db.close()
        
def saveCollection(context, collection):
    import library, mydb
    sql = "select ckey from collections where geek = %s and collectionindex = %s"
    ckeyData = mydb.query(sql,  [context.geek, collection.index])
    ckey = ckeyData[0][0]    
    collRow = library.Row()
    collRow.collectionname = collection.name
    collRow.description = collection.description
    collRow.collectionindex = collection.index
    collRow.geek = context.geek
    collRow.ckey = ckey
    mydb.saveRow(collRow, "collections", "ckey = %d" % ckey)
    mydb.update("delete from collectiongroups where ckey = %d" % ckey)
    for g in collection.groups:
        groupRow = library.Row()
        groupRow.ckey = ckey
        groupRow.groupname = g.name
        groupRow.groupindex = g.index
        groupRow.groupname = g.name
        groupRow.groupdesc = g.description        
        mydb.saveRow(groupRow, "collectiongroups", None)
    mydb.update("delete from collectiongames where ckey = %d and groupindex not in (select groupindex from collectiongroups where ckey = %d)" % (ckey, ckey))
            
