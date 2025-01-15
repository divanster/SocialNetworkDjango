# backend/kafka_app/schemas.py

from pydantic import BaseModel, Field
from typing import Dict, Any


class EventData(BaseModel):
    app: str = Field(..., description="Name of the Django app")
    event_type: str = Field(..., description="Type of the event")
    model_name: str = Field(..., description="Name of the model")
    id: str = Field(..., description="UUID of the object as a string")
    data: Dict[str, Any] = Field(..., description="Event-specific data")
