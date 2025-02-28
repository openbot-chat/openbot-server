from pydantic import BaseModel
from typing import TypeVar

class BaseSchema(BaseModel):
    # Pydantic V2 的新配置方式
    model_config = {
        'from_attributes': True,  # 替代原来的 orm_mode = True
        'populate_by_name': True  # 替代原来的 allow_population_by_field_name = True
    }

BASE_SCHEMA = TypeVar("BASE_SCHEMA", bound=BaseSchema)