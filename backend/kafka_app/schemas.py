# backend/kafka_app/schemas.py

from pydantic import BaseModel, Field, root_validator
from typing import Dict, Any, Optional


class EventData(BaseModel):
    app: str = Field(..., description="Name of the Django app")
    event_type: str = Field(..., description="Type of the event")
    model_name: str = Field(..., description="Name of the model")
    id: str = Field(..., description="UUID of the object as a string")
    data: Dict[str, Any] = Field(..., description="Event-specific data")

    @root_validator(pre=True)
    def check_event_type(cls, values):
        event_type = values.get('event_type')
        if not event_type:
            raise ValueError('event_type is required and cannot be None or empty')
        return values
