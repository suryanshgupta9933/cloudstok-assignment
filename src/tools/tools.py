import json
from typing import Dict, Any
from src.schemas.models import Order

# Mock Database
MOCK_ORDERS = {
    "123": {"order_id": "123", "status": "Shipped", "items": ["Laptop", "Mouse"], "delivery_date": "2025-12-12"},
    "456": {"order_id": "456", "status": "Processing", "items": ["Monitor"], "delivery_date": "2025-12-20"},
    "789": {"order_id": "789", "status": "Delivered", "items": ["Keyboard"], "delivery_date": "2025-11-25"},
}

def get_order_status(order_id: str) -> str:
    """
    Retrieves the status of an order given its Order ID.
    
    Args:
        order_id (str): The ID of the order to look up.
        
    Returns:
        str: A JSON string containing the order details or an error message.
    """
    order_data = MOCK_ORDERS.get(order_id)
    if order_data:
        # Validate with Pydantic model
        order = Order(**order_data)
        return json.dumps(order.model_dump())
    else:
        return json.dumps({"error": "Order not found."})

def escalate_to_human(reason: str) -> str:
    """
    Escalates the conversation to a human agent.
    
    Args:
        reason (str): The reason for escalation.
        
    Returns:
        str: Confirmation message.
    """
    return json.dumps({"status": "Escalated", "message": f"Ticket created. Reason: {reason}"})
