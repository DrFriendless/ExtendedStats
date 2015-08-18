# First test of using sqlite3 in memory to run unit tests
import sys
sys.path.append("..")

import stats.mydb as mydb
mydb.TESTING = True
db = mydb.get()
with open("simple.sql", "r") as scriptfile:
    lines = map(lambda s: s.strip(), scriptfile.readlines())
    text = "".join(lines)
    db.executescript(text)
cursor = db.execute("select * from files")
for row in cursor:
    print row
print "Done"