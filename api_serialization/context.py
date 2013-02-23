from json_writer import JSONWriter


class SerializationContext(object):
    def __init__(self, fields):
        super(SerializationContext, self).__init__()
        self.fields = fields

    def write(self, obj):
        load_ctx = LoadContext(fields=self.fields)
        # {object: {field: (model, key)}
        # {model: {key: object}}
        # {serialization_adapter: fields}
        graph, preloaded, fields = load_ctx.trace(obj)
        write_ctx = WriteContext(fields, graph, preloaded)
        write_ctx.write(obj)
        return write_ctx.build()


class LoadContext(object):
    def __init__(self, fields):
        super(LoadContext, self).__init__()
        self.fields = fields

    def trace(self, obj):
        return {}, {}, {"": self.fields}


class WriteContext(object):
    def __init__(self, fields, graph, preloaded):
        super(WriteContext, self).__init__()
        self.fields = fields
        self.graph = graph
        self.preloaded = preloaded
        self.writer = JSONWriter()
        self.path = ""

    def object(self):
        return self.writer.object()

    def write(self, obj):
        if hasattr(obj, "serialization_adapter"):
            orig_path = self.path
            try:
                with self.object():
                    for field in self.fields[self.path]:
                        self.path = orig_path + field
                        self.writer.write_key(field)
                        converter = obj.serialization_adapter.converters[field]
                        if obj in self.graph and field in self.graph[obj]:
                            model, key = self.graph[obj][field]
                            converter(obj, self, self.preloaded[model][key])
                        else:
                            converter(obj, self)
            finally:
                self.path = orig_path
        else:
            self.writer.write(obj)

    def build(self):
        return self.writer.build()
