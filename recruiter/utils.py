"""Helper functions for API
"""
from __future__ import unicode_literals
from collections import Iterable, OrderedDict
import json

from django.core.serializers.base import Serializer as BaseSerializer
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.json import Serializer as JsonSerializer
from django.db.models.query import QuerySet


class ReturnDict(OrderedDict):
    """
    Return object from `serializer.data` for the `Serializer` class.
    Includes a backlink to the serializer instance for renderers
    to use if they need richer field information.
    """

    def __init__(self, *args, **kwargs):
        self.serializer = kwargs.pop("serializer")
        super(ReturnDict, self).__init__(*args, **kwargs)

    def copy(self):
        return ReturnDict(self, serializer=self.serializer)

    def __repr__(self):
        return dict.__repr__(self)

    def __reduce__(self):
        # Pickling these objects will drop the .serializer backlink,
        # but preserve the raw data.
        return (dict, (dict(self),))


class ReturnList(list):
    """
    Return object from `serializer.data` for the `SerializerList` class.
    Includes a backlink to the serializer instance for renderers
    to use if they need richer field information.
    """

    def __init__(self, *args, **kwargs):
        self.serializer = kwargs.pop("serializer")
        super(ReturnList, self).__init__(*args, **kwargs)

    def __repr__(self):
        return list.__repr__(self)

    def __reduce__(self):
        # Pickling these objects will drop the .serializer backlink,
        # but preserve the raw data.
        return (list, (list(self),))


class ExtBaseSerializer(BaseSerializer):

    def serialize_property(self, obj):
        model = type(obj)
        for field in self.selected_fields:
            if hasattr(model, field) and type(getattr(model, field)) == property:
                self.handle_prop(obj, field)
            else:
                if not hasattr(model, field) and hasattr(obj, field):
                    self.handle_prop(obj, field)

    def handle_prop(self, obj, field):
        self._current[field] = getattr(obj, field)

    def end_object(self, obj):
        self.serialize_property(obj)

        super(ExtBaseSerializer, self).end_object(obj)


class ExtPythonSerializer(ExtBaseSerializer, PythonSerializer):
    pass


class Skinner(ExtPythonSerializer, JsonSerializer):

    def parse(self, queryset=[], fields=[], query=None):
        if isinstance(queryset, Iterable):
            serialized_data = json.loads(self.serialize(queryset, fields=fields))
        elif queryset:
            serialized_data = json.loads(self.serialize([queryset], fields=fields))
        else:
            serialized_data = None

        final_json_data = {}

        if (serialized_data is not None) and (not isinstance(queryset, QuerySet)):
            temp_serialized_data = serialized_data[0]
            temp_dict = temp_serialized_data["fields"]
            if "id" in fields:
                temp_dict["id"] = temp_serialized_data["pk"]
            final_json_data = temp_dict
        else:
            final_json_data = []
            for json_dict in serialized_data:
                temp_dict = json_dict["fields"]
                if "id" in fields:
                    temp_dict["id"] = json_dict["pk"]
                final_json_data.append(temp_dict)
        return {"data": final_json_data}
