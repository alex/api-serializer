from api_serialization import SerializationAdapter, SerializationContext


class TestConversion(object):
    def test_simple_convert(self):
        class Artist(object):
            serialization_adapter = SerializationAdapter()

            @serialization_adapter.converter("name")
            def convert_name(self, ctx):
                ctx.write("ABBA")

        ctx = SerializationContext(fields=["name"])
        assert ctx.write(Artist()) == '{"name":"ABBA"}'
