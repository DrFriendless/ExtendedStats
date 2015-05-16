#!/usr/bin/env python

import sys
sys.path.append(".")

BETWEEN_POPULATES = 300

def loadGameFiles():
    import time, populateFiles
    while True:
        finish = time.time() + BETWEEN_POPULATES
        populateFiles.main(False, finish)
        wait = finish - time.time()
        if wait > 0:
            print "Rest for", wait
            time.sleep(wait)

def readUserNames():
    import mydb, library
    db = mydb.get()
    usernames = library.dbexec(db, "select username from geeks")
    usernames = [ u[0] for u in usernames if len(u[0]) > 0 ]
    if "debug" in sys.argv:
        # testing
        usernames = debugUsers
        pass
    db.close()
    return usernames

import sys, mydb, sitedata
toFix = sys.argv[1:]
toFix = [ x for x in toFix if x != "debug" ]
debugUsers = sitedata.debugUsers + [ x for x in toFix if x not in sitedata.debugUsers ]
for geek in toFix:
    print mydb.update("update files set lastUpdate = null where geek = '%s' and processMethod != 'processGame'" % geek)
    print "Reset %s" % geek
while True:
    usernames = readUserNames()
    loadGameFiles()

