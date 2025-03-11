from typing import Generic, Sequence, Optional, ClassVar, TypeVar, Any
from fastapi import Query
from fastapi_pagination.bases import AbstractPage, AbstractParams, BaseRawParams
from fastapi_pagination.types import Cursor, ParamsType
from fastapi_pagination.cursor import decode_cursor, encode_cursor
from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing_extensions import Self

T = TypeVar("T")

class LimitOffsetPaginationParams:
  def __init__(self, limit: int = 20, offset: int = 0):
    self.limit = limit
    self.offset = offset


@dataclass
class CursorRawParams(BaseRawParams):
    cursor: Optional[Cursor]
    size: int
    type: ClassVar[ParamsType] = "cursor"
    need_total: Optional[bool] = True

class CursorParams(BaseModel, AbstractParams):
    cursor: Optional[str] = Query(None, description="Cursor for the next page")
    size: int = Query(50, ge=0, description="Page offset")
    need_total: Optional[bool] = Query(True, description="Need Total")

    str_cursor: ClassVar[bool] = True

    def to_raw_params(self) -> CursorRawParams:
        return CursorRawParams(
            cursor=decode_cursor(self.cursor, to_str=self.str_cursor),
            size=self.size,
            need_total=self.need_total,
        ) 


class CursorPage(AbstractPage[T], Generic[T]):
    items: Sequence[T]
    """
    current_page: Optional[str] = Field(None, description="Cursor to refetch the current page")
    current_page_backwards: Optional[str] = Field(
        None,
        description="Cursor to refetch the current page starting from the last item",
    )
    """
    previous_page: Optional[str] = Field(None, description="Cursor for the previous page")
    next_page: Optional[str] = Field(None, description="Cursor for the next page")
    total: Optional[int] = Field(None, description="Total count")

    __params_type__ = CursorParams

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        params: AbstractParams,
        *,
        next_: Optional[Cursor] = None,
        previous: Optional[Cursor] = None,
        total: Optional[int] = None,
        **kwargs: Any,
    ) -> Self:
        return cls(
            items=items,
            total=total,
            next_page=encode_cursor(next_),
            previous_page=encode_cursor(previous),
            **kwargs,
        )
  


