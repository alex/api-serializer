from json_writer import JSONWriter


class SerializationContext(object):
    def __init__(self, fields):
        super(SerializationContext, self).__init__()
        self.fields = fields

    def write(self, obj):
        load_ctx = LoadContext(fields=self.fields)
        # {object: {field: key}
        # {model: {key: object}}
        graph, preloaded = load_ctx.trace(obj)
        write_ctx = WriteContext(self.fields, graph, preloaded)
        write_ctx.write(obj)
        return write_ctx.build()


class LoadContext(object):
    def __init__(self, fields):
        super(LoadContext, self).__init__()
        self.fields = fields

    def trace(self, obj):
        return {}, {}


class WriteContext(object):
    def __init__(self, fields, graph, preloaded):
        super(WriteContext, self).__init__()
        self.fields = fields
        self.graph = graph
        self.preloaded = preloaded
        self.writer = JSONWriter()

    def object(self):
        return self.writer.object()

    def write(self, obj):
        if hasattr(obj, "serialization_adapter"):
            with self.object():
                for field in self.fields:
                    self.writer.write_key(field)
                    obj.serialization_adapter.converters[field](obj, self)
        else:
            self.writer.write(obj)

    def build(self):
        return self.writer.build()
