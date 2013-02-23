from api_serialization import SerializationAdapter, SerializationContext


class Artist(object):
    serialization_adapter = SerializationAdapter(base_fields=["name"])

    @serialization_adapter.converter("name")
    def convert_name(self, ctx):
        ctx.write("ABBA")


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
