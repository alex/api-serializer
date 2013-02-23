class SerializationAdapter(object):
    def __init__(self):
        super(SerializationAdapter, self).__init__()
        self.converters = {}

    def converter(self, name):
        assert name not in self.converters

        def inner(func):
            self.converters[name] = func
            return func
        return inner
