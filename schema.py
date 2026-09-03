from pydantic import BaseModel
from typing import Optional

class Project(BaseModel):
    project_name: str
    customer: str
    start_date: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "Active"
    notes: Optional[str] = None

class UserIntent(BaseModel):
    intent: str  # "create", "list", "get", "delete", "unclear"
    project_name: Optional[str] = None
    customer: Optional[str] = None
    missing_fields: Optional[list[str]] = []