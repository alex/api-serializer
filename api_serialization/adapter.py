class SerializationAdapter(object):
    def __init__(self, base_fields=None):
        super(SerializationAdapter, self).__init__()
        self.converters = {}
        self.base_fields = base_fields

    def converter(self, name):
        assert name not in self.converters

        def inner(func):
            self.converters[name] = func
            return func
        return inner
