class StrategyManager(object):
    def __init__(self):
        self.strategies = {}

    def register(self, type, loader):
        self.strategies[type] = loader
