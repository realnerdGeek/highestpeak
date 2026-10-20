# tiny patch helpers shared by the V7 build steps
class Doc:
    def __init__(self, s): self.s = s
    def rep(self, a, b, cnt=1):
        n = self.s.count(a)
        assert n == cnt, ('count %d != %d for: %s' % (n, cnt, a[:90]))
        self.s = self.s.replace(a, b)
    def cut(self, a, b, new):
        assert self.s.count(a) == 1, ('start not unique (%d): %s' % (self.s.count(a), a[:90]))
        i = self.s.index(a); j = self.s.index(b, i + len(a))
        self.s = self.s[:i] + new + self.s[j:]
    def before(self, a, new):
        assert self.s.count(a) == 1, ('anchor not unique (%d): %s' % (self.s.count(a), a[:90]))
        self.s = self.s.replace(a, new + a)
    def after(self, a, new):
        assert self.s.count(a) == 1, ('anchor not unique (%d): %s' % (self.s.count(a), a[:90]))
        self.s = self.s.replace(a, a + new)
