from pydantic import BaseModel, ConfigDict


class SelectOption(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: str | int
    label: str
    code: str | None = None
