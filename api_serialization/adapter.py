class SerializationAdapter(object):
    def __init__(self, base_fields=None):
        super(SerializationAdapter, self).__init__()
        self.base_fields = base_fields
        self.name = None
        self.converters = {}
        self.loaders = {}

    def converter(self, name):
        assert name not in self.converters

        def inner(func):
            self.converters[name] = func
            return func
        return inner

    def loader(self, name):
        assert name not in self.loaders

        def inner(func):
            self.loaders[name] = func
            return func
        return inner
