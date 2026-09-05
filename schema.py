from pydantic import BaseModel, Field
from typing import Optional, List

class Project(BaseModel):
    project_name: str
    customer: str
    start_date: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "Active"
    notes: Optional[str] = None

class UserIntent(BaseModel):
    intent: str = Field(description="Action intent: 'create', 'list', 'get', 'delete', or 'unclear'")
    project_name: Optional[str] = Field(None, description="Name of the project if mentioned")
    customer: Optional[str] = Field(None, description="Customer or client name if mentioned")
    start_date: Optional[str] = Field(None, description="Start date of the project (e.g., 31/10)")
    location: Optional[str] = Field(None, description="Location of the project")
    notes: Optional[str] = Field(None, description="Any extra notes or details provided")
    missing_fields: Optional[List[str]] = Field(default_factory=list, description="Mandatory fields that are missing for creation")