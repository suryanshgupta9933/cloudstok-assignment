import chainlit as cl
import httpx
import os
from src.helpers.utils import logger

# Backend API URL (default to localhost for local dev, override in docker)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

@cl.on_chat_start
async def start():
    await cl.Message(content="Hello! I am your Autonomous Customer Support Agent. How can I assist you today?").send()

@cl.on_message
async def main(message: cl.Message):
    # Create the message history for the agent
    messages = cl.user_session.get("messages", [])
    messages.append({"role": "user", "content": message.content})
    
    response_msg = cl.Message(content="")
    await response_msg.send()
    
    try:
        # Call the Backend API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/chat",
                json={"messages": messages}
            )
            response.raise_for_status()
            result = response.json()
            
        # Stream the response (simulated since we get full response)
        response_msg.content = result["response"]
        await response_msg.update()
        
        # Append assistant response to history
        messages.append({"role": "assistant", "content": result["response"]})
        cl.user_session.set("messages", messages)
        
        # Display tool calls if any
        if result.get("tool_calls"):
            for tool in result["tool_calls"]:
                async with cl.Step(name=tool["name"]) as step:
                    step.input = str(tool["args"])
                    step.output = str(tool["result"])
                    
    except Exception as e:
        logger.error(f"Error in UI: {e}")
        response_msg.content = f"An error occurred: {str(e)}"
        await response_msg.update()
