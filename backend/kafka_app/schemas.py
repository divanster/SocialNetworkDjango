from pydantic import BaseModel, Field, root_validator
from typing import Dict, Any, Optional


class EventData(BaseModel):
    app: str
    event_type: str
    model_name: str
    id: Optional[str] = None  # allow it to be missing
    data: Dict[str, Any]

    @root_validator(pre=True)
    def extract_id_from_data(cls, values):
        if not values.get("id") and "data" in values:
            values["id"] = values["data"].get("id")
        if not values.get("event_type"):
            raise ValueError("event_type is required")
        return values
