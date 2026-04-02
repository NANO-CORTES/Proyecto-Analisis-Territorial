from pydantic import BaseModel

class EventCreate(BaseModel):
    user_id: str
    action: str
    service_name: str
    status: str