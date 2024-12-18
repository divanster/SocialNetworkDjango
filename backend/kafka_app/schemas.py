# kafka_app/schemas.py

from pydantic import BaseModel, Field
from typing import Dict, Any


class KafkaMessage(BaseModel):
    app: str = Field(..., description="Name of the Django app")
    event_type: str = Field(..., description="Type of the event")
    data: Dict[str, Any] = Field(..., description="Event-specific data")
