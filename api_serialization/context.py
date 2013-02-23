from collections import defaultdict

from json_writer import JSONWriter


class SerializationContext(object):
    def __init__(self, fields=None, strategy_manager=None):
        super(SerializationContext, self).__init__()
        self.fields = fields
        self.strategy_manager = strategy_manager

    def write(self, obj):
        load_ctx = LoadContext(raw_fields=self.fields, strategy_manager=self.strategy_manager)
        graph, preloaded, fields = load_ctx.trace(obj)
        write_ctx = WriteContext(fields, graph, preloaded)
        write_ctx.write(obj)
        return write_ctx.build()


class LoadContext(object):
    def __init__(self, raw_fields, strategy_manager):
        super(LoadContext, self).__init__()
        self.raw_fields = raw_fields
        self.strategy_manager = strategy_manager
        self.needs_load = {}

        # {object: {field: (model, key)}
        self.graph = {}
        # {model: {key: object}}
        self.preloaded = {}
        # {path: [fields]}
        self.fields = {}

    def add_load(self, cls, key):
        if self.current_object not in self.graph:
            self.graph[self.current_object] = {}
        self.graph[self.current_object][self.current_field] = (cls, key)

        if cls not in self.needs_load:
            self.needs_load[cls] = set()
        if cls not in self.preloaded or key not in self.preloaded[key]:
            self.needs_load[cls].add((key, self.current_path))

    def trace(self, obj):
        self._trace(type(obj), [obj], "")
        while self.needs_load:
            cls, keys_and_paths = self.needs_load.popitem()
            path_to_key = defaultdict(list)
            keys = set()

            for key, path in keys_and_paths:
                path_to_key[path].append(key)
                keys.add(key)

            strategy = self.strategy_manager.strategies[type(cls)]
            keys_to_objects = strategy(keys)
            if cls not in self.preloaded:
                self.preloaded[cls] = {}
            for key, obj in keys_to_objects.iteritems():
                self.preloaded[cls][key] = obj
            for path, keys in path_to_key.iteritems():
                self._trace(cls, [keys_to_objects[key] for key in keys], path)
        return self.graph, self.preloaded, self.fields

    def _trace(self, cls, instances, path):
        if self.raw_fields is None:
            fields = cls.serialization_adapter.base_fields
        else:
            fields = []
            for field in self.raw_fields:
                if field.startswith(path):
                    partial_path = field[len(path):]
                    if partial_path[0] == ".":
                        partial_path = partial_path[1:]
                    if "." in partial_path:
                        fields.append(partial_path[:partial_path.index(".")])
                    else:
                        fields.append(partial_path)

        self.fields[path] = fields
        for field in fields:
            if field in cls.serialization_adapter.loaders:
                self.current_field = field
                self.current_path = (path + "." if path else path) + field
                for instance in instances:
                    self.current_object = instance
                    cls.serialization_adapter.loaders[field](instance, self)


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
                        self.path = (orig_path + "." if orig_path else orig_path) + field
                        self.writer.write_key(field)
                        converter = obj.serialization_adapter.converters[field]
                        if obj in self.graph and field in self.graph[obj]:
                            cls, key = self.graph[obj][field]
                            converter(obj, self, self.preloaded[cls][key])
                        else:
                            converter(obj, self)
            finally:
                self.path = orig_path
        else:
            self.writer.write(obj)

    def build(self):
        return self.writer.build()
