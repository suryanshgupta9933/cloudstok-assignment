import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

from src.schemas.models import AgentResult
from src.agents.prompts import SYSTEM_PROMPT
from src.tools.tools import get_order_status, escalate_to_human
from src.helpers.utils import log_execution, logger

load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Map tool names to functions
AVAILABLE_TOOLS = {
    "get_order_status": get_order_status,
    "escalate_to_human": escalate_to_human
}

# Define tool schemas for OpenAI
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get the status of an order given its Order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ID of the order, e.g., '123'."
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate the conversation to a human agent if the user is unhappy or the issue is complex.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "The reason for escalation."
                    }
                },
                "required": ["reason"]
            }
        }
    }
]

class Agent:
    def __init__(self, model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")):
        self.model = model
        self.system_prompt = SYSTEM_PROMPT

    @log_execution
    def run(self, messages: List[Dict[str, str]]) -> AgentResult:
        """
        Runs the agent loop:
        1. Appends system prompt if not present (handled by caller usually, but we ensure context).
        2. Calls LLM.
        3. If tool calls, execute them and recurse/loop.
        4. Return final response.
        """
        # Ensure system prompt is at the beginning if not already
        if not messages or messages[0]["role"] != "system":
            messages.insert(0, {"role": "system", "content": self.system_prompt})

        logger.info(f"Sending request to OpenAI with {len(messages)} messages.")
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )

        if response.usage:
            logger.info(f"Token Usage (First Call): Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}, Total: {response.usage.total_tokens}")

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Append the assistant's message with tool calls to history
            messages.append(response_message)
            
            executed_tools = []

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = AVAILABLE_TOOLS.get(function_name)
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"Agent decided to call tool: {function_name} with args: {function_args}")

                if function_to_call:
                    function_response = function_to_call(**function_args)
                    
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
                    executed_tools.append({"name": function_name, "args": function_args, "result": function_response})
            
            # Get a new response from the model where it can see the function response
            second_response = client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            if second_response.usage:
                logger.info(f"Token Usage (Second Call): Prompt: {second_response.usage.prompt_tokens}, Completion: {second_response.usage.completion_tokens}, Total: {second_response.usage.total_tokens}")
            final_content = second_response.choices[0].message.content
            
            return AgentResult(
                response=final_content,
                tool_calls=executed_tools
            )
        else:
            return AgentResult(response=response_message.content)

# Singleton instance or factory can be used
agent_instance = Agent()

def run_agent(messages: List[Dict[str, str]]) -> AgentResult:
    return agent_instance.run(messages)
