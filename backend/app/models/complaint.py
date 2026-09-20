from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ComplaintCreate(BaseModel):
    description: str = Field(min_length=5, max_length=2000)
    location: str = Field(min_length=2, max_length=300)
    category: str = Field(min_length=2, max_length=100)
    image_reference: str | None = Field(default=None, max_length=1000)


class Complaint(ComplaintCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
