import chainlit as cl
from src.agents.agent import run_agent
from src.helpers.utils import logger

@cl.on_chat_start
async def start():
    await cl.Message(content="Hello! I am your Autonomous Customer Support Agent. How can I assist you today?").send()

@cl.on_message
async def main(message: cl.Message):
    # Create the message history for the agent
    # In a real app, we'd maintain history in the session
    messages = cl.user_session.get("messages", [])
    messages.append({"role": "user", "content": message.content})
    
    response_msg = cl.Message(content="")
    await response_msg.send()
    
    try:
        # We'll run the agent in a separate thread to avoid blocking the async loop
        result = await cl.make_async(run_agent)(messages)
        
        # Stream the response (simulated since we get full response)
        response_msg.content = result.response
        await response_msg.update()
        
        # Append assistant response to history
        messages.append({"role": "assistant", "content": result.response})
        cl.user_session.set("messages", messages)
        
        # Display tool calls if any
        if result.tool_calls:
            for tool in result.tool_calls:
                async with cl.Step(name=tool["name"]) as step:
                    step.input = str(tool["args"])
                    step.output = str(tool["result"])
                    
    except Exception as e:
        logger.error(f"Error in UI: {e}")
        response_msg.content = f"An error occurred: {str(e)}"
        await response_msg.update()
