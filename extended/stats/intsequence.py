class IntSequence(object):
    pass
    
    def getCounts(self, context, opts, startDate, endDate):
        import library
        return library.Counts()
    
class PlayCountIntSequence(IntSequence):
    key = "playCount"
    arity = 0
    usesSelector = True

    def __init__(self, selector):
        self.selector = selector
        
    def getCounts(self, context, opts, startDate, endDate):
        import library
        games = self.selector.getGames(context, opts)
        plays = context.substrate.filterPlays(startDate, endDate)[0]
        result = library.AnnotatedCounts()
        for p in plays:
            include = (p.game in games)
            if not include:
                for e in p.expansions:
                    if e in games:
                        include = True
                        break
            if include:
                result.addAnnotated(p.dt, p.count, p.game.name)
        return result
        
class DistinctGamesPlayedIntSequence(IntSequence):
    key = "distinctGames"
    arity = 0
    usesSelector = True

    def __init__(self, selector):
        self.selector = selector
        
    def getCounts(self, context, opts, startDate, endDate):
        import library
        games = self.selector.getGames(context, opts)
        plays = context.substrate.filterPlays(startDate, endDate)[0]
        gamesPlayedByDate = {}        
        for p in plays:
            include = (p.game in games)   
            if include:
                already = gamesPlayedByDate.get(p.dt)
                if already is None:
                    already = []
                if p.game not in already:
                    already.append(p.game)
                gamesPlayedByDate[p.dt] = already
        result = library.AnnotatedCounts()
        for (date, already) in gamesPlayedByDate.items():
            for g in already:
                result.addAnnotated(date, 1, g.name)
        return result
        
INT_SEQUENCES = [ PlayCountIntSequence, DistinctGamesPlayedIntSequence ]

def parseIntSequence(fields):
    import selectors
    key = fields[0]
    fields = fields[1:]
    for seq in INT_SEQUENCES:
        if key == seq.key:
            args = fields[:seq.arity]
            fields = fields[seq.arity:]
            if seq.usesSelector:
                sel = selectors.getSelectorFromFields(fields)
                args.append(sel)
            return apply(seq, args)
    raise selectors.UnknownSymbol(key)
    
