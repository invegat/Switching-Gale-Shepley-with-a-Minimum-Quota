from collections import defaultdict


class Matcher:

    def __init__(self, men, women, forbidden):
        '''
        Constructs a Matcher instance.

        Takes a dict of men's spousal preferences, `men`,
        a dict of women's spousal preferences, `women`,
        and a dict specifying which marriages are forbidden
        for each man:

        >>> forbidden = { 'dan': ['ann', 'eve', ... ] }

        '''
        self.M = men
        self.W = women
        self.forbidden = forbidden
        self.wives = {}
        self.pairs = []

        # we index spousal preferences at initialization
        # to avoid expensive lookups when matching
        self.mrank = defaultdict(dict)  # `mrank[m][w]` is m's ranking of w
        self.wrank = defaultdict(dict)  # `wrank[w][m]` is w's ranking of m

        for m, prefs in men.items():
            for i, w in enumerate(prefs):
                self.mrank[m][w] = i

        for w, prefs in women.items():
            for i, m in enumerate(prefs):
                self.wrank[w][m] = i

        # for m, prefs in men.items():
        #     for i, w_ in enumerate(prefs):
        #         w = list(filter(lambda w: w.n == w_, woman))[0]
        #         self.mrank[m][w] = i

        # for w, prefs in women.items():
        #     for i, m_ in enumerate(prefs):
        #         m = list(filter(lambda w: w.n == m_, men))[0]
        #         self.wrank[w][m] = i

    def __call__(self):
        return self.match()

    def prefers(self, w, m, h):
        '''
        Test whether w prefers m over h.

        '''
        return self.wrank[w][m] < self.wrank[w][h]

    def is_forbidden(self, m, w):
        '''
        Test whether (m, w) is a forbidden pairing.

        '''
        return w in self.forbidden.get(m, [])

    def after(self, m, w):
        '''
        Return the woman favored by m after w.

        '''
        prefs = self.M[m]               # m's ordered list of preferences
        # index of woman following w in list of prefs
        i = self.mrank[m][w] + 1
        if i >= len(prefs):
            return ''                   # no more women left!
        w = prefs[i]                    # woman following w in list of prefs
        if self.is_forbidden(m, w):     # if (m, w) is forbidden
            return self.after(m, w)     # try next w
        return w

    def match(self, men=None, next=None, wives=None):
        '''
        Try to match all men with their next preferred spouse.

        '''
        if men is None:
            men = self.M.keys()         # get the complete list of men
        if next is None:
            # if not defined, map each man to their first preference
            next = dict((m, rank[0]) for m, rank in self.M.items())
        if wives is None:
            wives = {}                  # mapping from women to current spouse
        if not len(men):
            self.pairs = [(h, w) for w, h in wives.items()]
            self.wives = wives
            return wives
        lmen = list(men)
        m, men = lmen[0], lmen[1:]
        w = next[m]                     # next woman for m to propose to
        if not w:                       # continue if no woman to propose to
            return self.match(men, next, wives)
        next[m] = self.after(m, w)      # woman after w in m's list of prefs
        if w in wives:
            h = wives[w]                # current husband
            if self.prefers(w, m, h):
                men.append(h)           # husband becomes available again
                wives[w] = m            # w becomes wife of m
            else:
                men.append(m)           # m remains unmarried
        else:
            wives[w] = m                # w becomes wife of m
        return self.match(men, next, wives)

    def is_stable(self, wives=None, verbose=False):
        if wives is None:
            wives = self.wives
        for w, m in wives.items():
            i = self.M[m].index(w)
            preferred = self.M[m][:i]
            for p in preferred:
                if p in self.forbidden.get(m, []):  # no need to worry about
                    continue                        # forbidden marriages@
                if p not in wives:
                    continue
                h = wives[p]
                if self.W[p].index(m) < self.W[p].index(h):
                    msg = "{}'s marriage to {} is unstable: " + \
                          "{} prefers {} over {} and {} prefers " + \
                          "{} over her current husband {}"
                    if verbose:
                        print(msg.format(m.n, w.n, m.n, p.n, w.n, p.n, m.n, h.n))
                    return False
        return True
