from api_serialization import SerializationAdapter, SerializationContext, StrategyManager

from .utils import FakeStrategy


class Album(object):
    serialization_adapter = SerializationAdapter(base_fields=["name"])

    def __init__(self, artist):
        super(Album, self).__init__()
        self.artist = artist

    @serialization_adapter.loader("artist")
    def load_artist(self, ctx):
        ctx.add_load(Artist, self.artist)

    @serialization_adapter.converter("artist")
    def convert_artist(self, ctx, artist):
        ctx.write(artist)


class Artist(object):
    serialization_adapter = SerializationAdapter(base_fields=["name"])

    @serialization_adapter.converter("name")
    def convert_name(self, ctx):
        ctx.write("ABBA")

    @serialization_adapter.converter("play_count")
    def convert_play_count(self, ctx):
        ctx.write(1000)


class TestConversion(object):
    def test_simple_convert(self):
        ctx = SerializationContext(fields=["name"])
        assert ctx.write(Artist()) == '{"name":"ABBA"}'

    def test_no_fields(self):
        ctx = SerializationContext(fields=[])
        assert ctx.write(Artist()) == "{}"

    def test_base_fields(self):
        ctx = SerializationContext()
        assert ctx.write(Artist()) == '{"name":"ABBA"}'

    def test_nested_field(self):
        manager = StrategyManager()
        manager.register(type, FakeStrategy())
        ctx = SerializationContext(fields=["artist.play_count"], strategy_manager=manager)
        album = Album(Artist())
        assert ctx.write(album) == '{"artist":{"play_count":1000}}'
