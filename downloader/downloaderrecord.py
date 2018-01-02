class DownloaderRecord(object):
    def __init__(self):
        self.filesprocessed = 0
        self.waittime = 0.0
        self.pausetime = 0.0
        self.nothing = 0.0
        self.failures = 0
        self.tryagains = 0
        self.games = 0
        self.users = 0
        self.endtime = None
        self.startime = None
        self.files1 = 0
        self.files2 = 0
        self.files3 = 0

    def usersAndGames(self, u, g):
        self.users = u
        self.games = g

    def __enter__(self):
        import time
        self.starttime = time.time()
        return self

    def finish(self):
        import time
        self.endtime = time.time()

    def __exit__(self, type, value, tb):
        pass

    def wait(self, howlong):
        self.waittime += howlong

    def pause(self, howlong):
        self.pausetime += howlong

    def nothingToDo(self, howlong):
        self.nothing += howlong

    def processFiles(self, n):
        self.filesprocessed = self.filesprocessed + n

    def failure(self):
        self.failures += 1

    def tryagain(self):
        self.tryagains += 1

    def toSQL(self):
        import time
        format = '%Y-%m-%d %H:%M:%S'
        return "insert into downloader (starttime, endtime, filesprocessed, waittime, pausetime, nothing, failures, users, games, files1, files2, files3, tryagains) values ('%s', '%s', %d, %6.2f, %6.2f, %6.2f, %d, %d, %d, %d, %d, %d, %d)" % (time.strftime(format, time.localtime(self.starttime)), time.strftime(format, time.localtime(self.endtime)), self.filesprocessed, self.waittime, self.pausetime, self.nothing, self.failures, self.users, self.games, self.files1, self.files2, self.files3, self.tryagains)

    def __str__(self):
        import time
        return "From %s to %s, %d users %d games %d files %d failures %d tryagains %4.1f wait %4.1f pause %4.1f nothing to do" % (time.ctime(self.starttime), time.ctime(self.endtime), self.users, self.games, self.filesprocessed, self.failures, self.tryagains, self.waittime, self.pausetime, self.nothing)
