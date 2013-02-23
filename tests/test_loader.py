from api_serialization import SerializationAdapter, SerializationContext, StrategyManager


class Artist(object):
    serialization_adapter = SerializationAdapter(base_fields=["name"])

    def __init__(self, name):
        super(Artist, self).__init__()
        self.name = name

    @serialization_adapter.converter("name")
    def convert_name(self, ctx):
        ctx.write(self.name)


class Album(object):
    serialization_adapter = SerializationAdapter(base_fields=["artist"])

    def __init__(self, artist):
        super(Album, self).__init__()
        self.artist = artist

    @serialization_adapter.loader("artist")
    def load_artist(self, ctx):
        ctx.add_load(Artist, self.artist)

    @serialization_adapter.converter("artist")
    def convert_artist(self, ctx, artist):
        ctx.write(artist)


class TestLoader(object):
    def test_simple_load(self):
        manager = StrategyManager()
        manager.register(type, lambda keys: dict((k, k) for k in keys))
        ctx = SerializationContext(strategy_manager=manager)
        album = Album(artist=Artist("ABBA"))
        assert ctx.write(album) == '{"artist":{"name":"ABBA"}}'
