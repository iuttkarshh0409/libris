from typing import Generic, TypeVar

T = TypeVar("T")


class Result(Generic[T]):
    """Monadic Result object representing either a Success or a Failure."""

    def __init__(
        self,
        is_success: bool,
        value: T | None = None,
        error: Exception | None = None,
    ) -> None:
        self._is_success = is_success
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    @property
    def value(self) -> T:
        if not self._is_success:
            raise ValueError("Cannot access value of a failed Result.")
        assert self._value is not None
        return self._value

    @property
    def error(self) -> Exception:
        if self._is_success:
            raise ValueError("Cannot access error of a successful Result.")
        assert self._error is not None
        return self._error


class Success(Result[T]):
    """Represents a successful computation outcome containing a value."""

    def __init__(self, value: T) -> None:
        super().__init__(is_success=True, value=value)


class Failure(Result[T]):
    """Represents a failed computation outcome containing an exception."""

    def __init__(self, error: Exception) -> None:
        super().__init__(is_success=False, error=error)
