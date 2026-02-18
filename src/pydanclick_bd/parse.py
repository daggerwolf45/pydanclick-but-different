import re
import datetime
from enum import EnumType
from typing import TYPE_CHECKING
from uuid import UUID

import click
import annotated_types


if TYPE_CHECKING:
    from pydantic._internal._model_construction import ModelMetaclass
    from pydantic.fields import FieldInfo

BASIC_CLICK_TYPES = [
    str,
    bool,
    UUID,
]


def parse_type(field: "FieldInfo") -> type | click.ParamType:
    # print(f"Parsing: {type(field.annotation)}:{field.annotation}")
    if field.annotation in BASIC_CLICK_TYPES:
        return field.annotation
    if field.annotation in [int, float]:
        if field.metadata:
            min_max = {}
            for data in field.metadata:
                match type(data):
                    case annotated_types.Ge:
                        min_max["min"] = data.ge
                    case annotated_types.Gt:
                        min_max["min"] = data.gt
                        min_max["min_open"] = True
                    case annotated_types.Le:
                        min_max["max"] = data.le
                    case annotated_types.Lt:
                        min_max["max"] = data.lt
                        min_max["max_open"] = True
            if min_max != {}:
                if field.annotation is int:
                    return click.IntRange(**min_max)
                return click.FloatRange(**min_max)

        return field.annotation
    if type(field.annotation) is EnumType:
        return click.Choice(field.annotation)
    if field.annotation is datetime.datetime or datetime.date:
        return click.DateTime()
    return click.STRING


camel_match = re.compile(r"(?<!^)(?=[A-Z])")
