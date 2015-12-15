import json

from .json import JSONSerializer


def json_serialize(obj, **options):
    json_serializer = JSONSerializer()
    return json_serializer.serialize(obj, **options)


def json_deserialize(obj, **options):
    return json.loads(obj)