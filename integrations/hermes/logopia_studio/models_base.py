"""Strict wire primitives shared by the native workflow boundaries."""

from typing import Annotated, ClassVar, Final, Literal, TypeAlias

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, JsonValue, TypeAdapter
from typing_extensions import override

EDIT_LIMIT: Final = 2
INITIAL_IMAGE_LIMIT: Final = 9
CRITIQUE_LIMIT: Final = 2
ROLE_COUNT: Final = 2
CRITERION_COUNT: Final = 5
REQUEST_LIMIT: Final = 32768

Identifier: TypeAlias = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")]
Digest: TypeAlias = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
Text: TypeAlias = Annotated[str, Field(min_length=1, max_length=2000)]
Note: TypeAlias = Annotated[str, Field(max_length=2000)]
Prompt: TypeAlias = Annotated[str, Field(min_length=1, max_length=20000)]
Receipt: TypeAlias = Annotated[str, Field(max_length=64000)]
Count: TypeAlias = Annotated[int, Field(ge=1, le=6)]
Revision: TypeAlias = Annotated[int, Field(ge=0)]
Background: TypeAlias = Literal["opaque", "transparent"]
Role: TypeAlias = Literal["design", "production"]
CriterionKey: TypeAlias = Literal["text", "composition", "small_size", "preservation", "background"]


class StudioError(ValueError):
    """Typed errors that can safely cross the tool and launcher boundary."""

    code: str
    detail: str
    raw_reports: tuple[str, ...]

    def __init__(self, code: str, detail: str, raw_reports: tuple[str, ...] = ()) -> None:
        self.code = code
        self.detail = detail
        self.raw_reports = raw_reports
        super().__init__(detail)

    @override
    def __str__(self) -> str:
        return f"{self.code}: {self.detail}"


_SCHEMA_INTEGER: Final = TypeAdapter(int, config=ConfigDict(strict=True))


def schema_integer(value: JsonValue) -> int:
    return _SCHEMA_INTEGER.validate_python(value)


SchemaVersion: TypeAlias = Annotated[Literal[1], BeforeValidator(schema_integer)]


class FrozenModel(BaseModel):
    """Reject coercion, unknown fields and mutable external records."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True, strict=True, extra="forbid", validate_default=True
    )
