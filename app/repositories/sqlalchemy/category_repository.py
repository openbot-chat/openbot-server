from typing import Type
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from .category import Category
from repositories.sqlalchemy.base_repository import BaseRepository



from models.category import (
    CreateCategorySchema,
    UpdateCategorySchema,
    CategorySchema,
)

class CategoryRepository(BaseRepository[
    CreateCategorySchema,
    UpdateCategorySchema,
    CategorySchema,
    Category,
]):
    @property
    def _table(self) -> Type[Category]:
        return Category

    @property
    def _schema(self) -> Type[CategorySchema]:
        return CategorySchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Category.created_at)