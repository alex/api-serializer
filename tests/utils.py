class FakeStrategy(object):
    def load(self, keys):
        return dict((k, k) for k in keys)
