from typing import Any


class ValueObject:
    """Base class for all Value Objects.

    Value Objects are defined by their attributes rather than a thread of identity.
    They are immutable.
    """

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ValueObject):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))


class Identifier(ValueObject):
    """Immutable unique identifier value object."""

    def __init__(self, value: str) -> None:
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r})"


class BaseEntity:
    """Base class for all domain entities.

    Entities have a distinct identity that persists over time.
    """

    def __init__(self, id: Identifier) -> None:
        self._id = id

    @property
    def id(self) -> Identifier:
        return self._id

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
