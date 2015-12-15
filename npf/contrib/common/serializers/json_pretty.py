import json

from django.core.serializers.json import Serializer as JSONSerializer, Deserializer as JSONDeserializer, \
    DjangoJSONEncoder


class Serializer(JSONSerializer):
    def end_object(self, obj):
        # self._current has the field data
        indent = self.options.get("indent")
        if not self.first:
            self.stream.write(",")
            if not indent:
                self.stream.write(" ")
        if indent:
            self.stream.write("\n")
        json.dump(self.get_dump_object(obj), self.stream,
                  cls=DjangoJSONEncoder, ensure_ascii=False, **self.json_kwargs)
        self._current = None


Deserializer = JSONDeserializer 