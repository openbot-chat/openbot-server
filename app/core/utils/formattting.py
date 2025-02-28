"""Utilities for formatting strings."""
from string import Formatter
from typing import Any, List, Mapping, Sequence, Union



class FormatDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

class UnstrictFormatter(Formatter):
    """A subclass of formatter that checks for extra keys."""

    def vformat(
        self, format_string: str, args: Sequence, kwargs: Mapping[str, Any]
    ) -> str:
        """Check that no arguments are provided."""
        kkwargs = FormatDict(**kwargs)

        return super().vformat(format_string, args, kkwargs)


unstrict_formatter = UnstrictFormatter()