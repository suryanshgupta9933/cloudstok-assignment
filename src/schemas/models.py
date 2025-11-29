from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Order(BaseModel):
    order_id: str
    status: str
    items: List[str]
    delivery_date: Optional[str] = None

class Customer(BaseModel):
    customer_id: str
    name: str
    email: str

class AgentResult(BaseModel):
    """Result returned by the agent after processing."""
    response: str
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    source_agent: str = "CustomerSupportAgent"
