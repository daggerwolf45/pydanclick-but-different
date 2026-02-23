# Pydanclick (but-different)
> Generate [Click](https://click.palletsprojects.com/en/stable/) options from [Pydantic](https://github.com/pydantic/pydantic) models

Inspired by the original (and fantastic) [Pydanclick](https://felix-martel.github.io/pydanclick/) by [*Felix Martel*](https://github.com/felix-martel), writen from scratch without the use of AI.

### Differences from Pydanclick
* Uses Field extra data for overrides, rather than passing through the decorator
* Written by Sam Laird as opposed to Felix Martel

### Yet to be implemented/TODO
* Nested Model
* Object Unpacking
* Validation/testing

# Installation / Basic Usage
Install via pip/uv/your_package_manager_of_choice
```shell
pip install pydanclick-but-different
```
To then use simply call the `pydantic_option` decorator with your pydantic model, on a click endpoint
```python
from pydanclick-bd import pydantic_option

class MyEnum(Enum):
    RedPill = auto()
    BluePill = auto()

class MyModel(BaseModel):
    foo: str = Field(description="Help string goes here. Foo is optional since it has a default", default="Bazinga")
    bar: int = Field(description="Gt/lt operators are supported", gt=69, le= 420)
    choice: MyEnum = Field(description="Enums are converted to choice options. Anything can be prompted with prompt", prompt=True)
    hidden: int = Field(description="This will not be shown in help", hidden=True)
    shit: bool = Field(description="Alias' are also supported", validation_alias="poop")

@click.command()
@pydantic_option(MyModel)
@pydantic_option(MyOtherModel, 'named_something_unique')
def cli(mymodel: MyModel, named_something_unique: MyOtherModel):
    # your click method here
    ...
```
```
~ python click_app.py --help
Usage: click_app.py [OPTIONS]

Options:
  --poop BOOLEAN               Alias' are also supported  [required]
  --choice [RedPill|BluePill]  Enums are converted to choice options. Anything
                               can be prompted with prompt  [required]
  --bar INTEGER RANGE          Gt/lt operators are supported  [69<x<=420;
                               required]
  --foo TEXT                   Help string goes here. Foo is optional since it
                               has a default
  --help                       Show this message and exit. 
```


## Details
### Supported types
| Field Type                            | Passed as       |
| :--------------------------------------- | :------------------- |
| `bool`                                   | `click.BOOL`         |
| `str`                                    | `click.STRING`       |
| `int`                                    | `click.INT`          |
| `float`                                  | `click.FLOAT`        |
| `pathlib.Path`                           | `click.Path()`       |
| `UUID`                                   | `click.UUID`         |
| `datetime`, `date`                       | `click.DateTime()`   |
| `Enum`                                   | `click.Choice`       |

### Supported Field Flags
| Field(...) parameter | Description |
| :------------------- | :---------- |
| `description`          | Help string |
| `required`            | Explicitly mark field as required (default) |
| `alias`, `validation_alias` | Use as `Option` name |
| `hidden`              | Hide field from help message |
| `default`             | Default value/mark un-required |
| `gt/ge/lt/le`         | Use specified range (Note, this passes as `<int\|float>Range()`)
| `prompt`              | Prompt user for input if option is not provided. |
| `hide_input`          | Hide's user input if prompted (password mode)