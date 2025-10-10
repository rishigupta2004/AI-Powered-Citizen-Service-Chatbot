from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EndpointResponse(BaseModel):
    status: str = Field(default="not_implemented")
    links: List[str] = Field(default_factory=list)
    data: Optional[Dict[str, Any]] = None


class SearchQuery(BaseModel):
    q: str
    service_id: Optional[int] = None
    limit: int = 10


class SuggestionQuery(BaseModel):
    q: str
    limit: int = 5


class AnalyticsEvent(BaseModel):
    event_type: str
    user_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class AdminContentRequest(BaseModel):
    type: str
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class BackupRequest(BaseModel):
    scope: str = "all"
    destination: Optional[str] = None


class RestoreRequest(BaseModel):
    source: str