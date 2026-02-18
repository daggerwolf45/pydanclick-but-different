from functools import wraps
from typing import TYPE_CHECKING

import click
from pydanclick_bd.parse import camel_match, parse_type
from pydantic import AliasChoices
from pydantic_core import PydanticUndefined


if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic._internal._model_construction import ModelMetaclass


def pydantic_option(
    options: "ModelMetaclass", variable_name: str | None = None
) -> "Callable":
    if variable_name is None:
        variable_name = camel_match.sub("_", options.__name__).lower()

    def wrapper(func):
        for field, data in options.model_fields.items():
            option_kw = {"type": parse_type(data)}
            name = field.lower()

            # Help String
            if data.description:
                option_kw["help"] = data.description
            # Defaults & Required option
            if data.default and data.default is not PydanticUndefined:
                option_kw["default"] = data.default
            elif data.is_required:
                option_kw["required"] = True
            # Environment
            env_var = []
            if data.validation_alias:
                if isinstance(data.validation_alias, AliasChoices):
                    env_var.extend(data.validation_alias.choices)
                else:
                    env_var += data.validation_alias
                    name = data.validation_alias
            elif data.alias:
                env_var = [data.alias]
                name = data.alias
            else:
                env_var = field
            # Prompt
            if data.json_schema_extra is not None:
                if "prompt" in data.json_schema_extra:
                    option_kw["prompt"] = data.json_schema_extra["prompt"]
                if "hide_input" in data.json_schema_extra:
                    option_kw["hide_input"] = data.json_schema_extra["hide_input"]
                if "hidden" in data.json_schema_extra:
                    option_kw["hidden"] = data.json_schema_extra["hidden"]

            option_kw["envvar"] = env_var

            func = click.option(f"--{name}", **option_kw)(func)

        @wraps(func)
        def wraped(*args, **kw):
            builder = {}
            for field, data in options.model_fields.items():
                if field in kw:
                    if kw[field] is not None:
                        # Undo click alias correction correctly for pydantic
                        if data.validation_alias:
                            if isinstance(data.validation_alias, AliasChoices):
                                ref = data.validation_alias.choices[0]
                            else:
                                ref = data.validation_alias
                        elif data.alias:
                            ref = data.alias
                        else:
                            ref = field

                        builder[ref] = kw[field]
                    kw.pop(field)
                elif data.validation_alias is not None and data.validation_alias in kw:
                    builder[data.validation_alias] = kw.pop(data.validation_alias)

            model = options.model_validate(builder)

            data = {variable_name: model}

            return func(*args, **kw, **data)

        return wraped

    return wrapper
