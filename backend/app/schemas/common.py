from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20
    sort_by: str = "created_at"
    order: str = "asc"
    search: str = ""


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationMeta


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str = "Success"


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
