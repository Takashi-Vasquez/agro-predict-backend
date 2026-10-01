from pydantic import BaseModel, ConfigDict, Field


class CatalogDetailRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    value: str
    label: str
    order_index: int = Field(alias="orderIndex")


class CatalogRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    label: str
    description: str | None = None
    details: list[CatalogDetailRead] = []
