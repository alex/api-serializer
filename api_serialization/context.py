from json_writer import JSONWriter


class SerializationContext(object):
    def __init__(self, fields=None, strategy_manager=None):
        super(SerializationContext, self).__init__()
        self.fields = fields
        self.strategy_manager = strategy_manager

    def compile_fields(self):
        return Fields(self.fields)

    def write(self, obj):
        compiled_fields = self.compile_fields()
        load_ctx = LoadContext(fields=compiled_fields, strategy_manager=self.strategy_manager)
        graph, preloaded = load_ctx.trace(obj)
        write_ctx = WriteContext(compiled_fields, graph, preloaded)
        write_ctx.write(obj, root=True)
        return write_ctx.build()


class Fields(object):
    def __init__(self, raw_fields):
        root_fields = None
        fields = {}
        if raw_fields is not None:
            for field in raw_fields:
                if "." in field:
                    cls_name, field = field.split(".")
                    fields.setdefault(cls_name, []).append(field)
                else:
                    if root_fields is None:
                        root_fields = []
                    root_fields.append(field)
        self.root_fields = root_fields
        self.fields = fields

    def get_fields_for_class(self, cls, root):
        has_fields = False
        fields = []
        if root and self.root_fields is not None:
            has_fields = True
            fields.extend(self.root_fields)
        if cls.__name__ in self.fields:
            has_fields = True
            fields.extend(self.fields[cls.__name__])
        if cls.serialization_adapter.name in self.fields:
            has_fields = True
            fields.extend(self.fields[cls.serialization_adapter.name])
        if not has_fields:
            return cls.serialization_adapter.base_fields
        return fields


class LoadContext(object):
    def __init__(self, fields, strategy_manager):
        super(LoadContext, self).__init__()
        self.fields = fields
        self.strategy_manager = strategy_manager
        self.needs_load = {}

        # {object: {field: (model, key)}
        self.graph = {}
        # {model: {key: object}}
        self.preloaded = {}

    def add_load(self, cls, key):
        if self.current_object not in self.graph:
            self.graph[self.current_object] = {}
        self.graph[self.current_object][self.current_field] = (cls, key)

        if cls not in self.preloaded or key not in self.preloaded[key]:
            self.needs_load.setdefault(cls, set()).add(key)

    def trace(self, obj):
        self._trace(type(obj), [obj], root=True)
        while self.needs_load:
            cls, keys = self.needs_load.popitem()
            strategy = self.strategy_manager.strategies[type(cls)]
            keys_to_objects = strategy.load(keys)

            preloaded = self.preloaded.setdefault(cls, {})
            for key, obj in keys_to_objects.iteritems():
                preloaded[key] = obj
            self._trace(cls, keys_to_objects.itervalues())
        return self.graph, self.preloaded

    def _trace(self, cls, instances, root=False):
        fields = self.fields.get_fields_for_class(cls, root=root)

        for field in fields:
            if field in cls.serialization_adapter.loaders:
                loader = cls.serialization_adapter.loaders[field]
                self.current_field = field
                for instance in instances:
                    self.current_object = instance
                    loader(instance, self)


class WriteContext(object):
    def __init__(self, fields, graph, preloaded):
        super(WriteContext, self).__init__()
        self.fields = fields
        self.graph = graph
        self.preloaded = preloaded
        self.writer = JSONWriter()

    def object(self):
        return self.writer.object()

    def array(self):
        return self.writer.array()

    def write(self, obj, root=False):
        if hasattr(obj, "serialization_adapter"):
            with self.object():
                fields = self.fields.get_fields_for_class(type(obj), root=root)
                for field in fields:
                    self.writer.write_key(field)
                    converter = obj.serialization_adapter.converters[field]
                    if obj in self.graph and field in self.graph[obj]:
                        cls, key = self.graph[obj][field]
                        converter(obj, self, self.preloaded[cls][key])
                    else:
                        converter(obj, self)
        else:
            self.writer.write(obj)

    def build(self):
        return self.writer.build()
