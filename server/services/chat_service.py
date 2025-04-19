# server/services/chat_service.py

"""
Chat Service Module
-------------------
This module provides the core logic for handling chat interactions with the OpenAI API, including:
- Preparing system and time context messages
- Managing conversation history
- Calling the OpenAI ChatCompletion API
- Logging API requests and responses
- Calculating token usage and cost
- Storing analytics and error logs

Functions:
    get_system_message(): Returns the default system prompt for the assistant.
    get_time_context_message(): Returns a system message with the current EST time.
    process_chat(user_message, conversation_history, user_id=None):
        Handles a user chat message, manages conversation state, calls the LLM, logs analytics, and returns the response.
"""

# Standard library imports
import os  # For environment variable access
import json  # For JSON serialization
from datetime import datetime  # For timestamping
import pytz  # For timezone handling

# Third-party imports
from openai import OpenAI  # OpenAI API client

# Internal module imports
from helpers.token_utils import calculate_token_cost  # Token cost calculation utility
from services.analytics_service import store_request_analytics, store_openai_api_log  
from models.sql_models import OpenAIAPILog  # Database model for API logs
from database.session import ScopedSession  # Database session management
from helpers.rag_helpers import search_cfr_documents, search_m21_documents

# Initialize the OpenAI client with the API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# The model used for chat completions
model = "gpt-4.1-nano-2025-04-14"



tools = [
    {
        "type": "function",
        "name": "cfr_search",
        "description": (
            "Search 38 CFR regulations. "
            "Transforms the user query, generates embeddings, and retrieves relevant CFR sections "
            "using a Pinecone search."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The user query for searching 38 CFR regulations."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "m21_search",
        "description": (
            "Search the M21 Manual of VA Regulations. "
            "Transforms the user query, generates embeddings, and retrieves relevant articles "
            "using a Pinecone search."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The user query for searching the M21 Manual."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
]

def get_system_message():
    """
    Return the system message for the chat assistant.
    This message sets the assistant's behavior/personality for the conversation.
    """
    return {
        "role": "system",
        "content": (
            """ 
            # Identity
            
            """
        )
    }


def get_time_context_message():
    """
    Get the current time in EST and return a time context message for the chat.
    This message provides the assistant with the current time context in the conversation.
    """
    try:
        # Get current time in EST using pytz
        est = pytz.timezone('US/Eastern')
        current_time = datetime.now(est)
        current_time_formatted = current_time.strftime('%Y-%m-%d %H:%M:%S EST')
    except Exception as e:
        # Fallback to manual calculation if pytz fails
        from datetime import datetime, timedelta
        utc_now = datetime.utcnow()
        est_offset = timedelta(hours=-5)
        est_time = utc_now + est_offset
        current_time_formatted = est_time.strftime('%Y-%m-%d %H:%M:%S EST')
    return {
        "role": "system",
        "content": f"Current time: {current_time_formatted}"
    }


def process_chat(user_message, conversation_history, user_id=None):
    """
    Process a chat message and return the assistant's response.
    Handles conversation history, system/time context, OpenAI API call, logging, and analytics.
    Args:
        user_message (str): The user's message to the assistant.
        conversation_history (list): The list of previous messages in the conversation.
        user_id (optional): The ID of the user (for logging/analytics).
    Returns:
        tuple: (response dict, HTTP status code)
    """
    print("[DEBUG] Starting process_chat function")
    if not user_message:
        print("[DEBUG] No user message provided")
        return {"error": "No 'message' provided"}, 400

    # Ensure conversation_history is a list
    if not isinstance(conversation_history, list):
        print("[DEBUG] conversation_history is not a list, initializing as an empty list")
        conversation_history = []

    # Check if the conversation history already has a system message
    has_system_message = any(
        msg.get("role") == "system" and "You are a helpful assistant" in msg.get("content", "")
        for msg in conversation_history
    )
    print(f"[DEBUG] System message present: {has_system_message}")

    # If no conversation history or no system message, add the system message
    if not conversation_history or not has_system_message:
        print("[DEBUG] Adding system message to conversation history")
        conversation_history.insert(0, get_system_message())

    # Check if there's a time context message in the conversation history
    has_time_context = any(
        msg.get("role") == "system" and "Current time:" in msg.get("content", "")
        for msg in conversation_history
    )
    print(f"[DEBUG] Time context message present: {has_time_context}")

    # If no time context message, add one
    if not has_time_context:
        print("[DEBUG] Adding time context message to conversation history")
        conversation_history.append(get_time_context_message())

    # Record start time for latency tracking
    start_time = datetime.utcnow()
    print("[DEBUG] Start time recorded")

    # Add tools to the request payload
    request_payload = {
        "model": model,
        "messages": conversation_history,
        "max_completion_tokens": 750,
        "functions": tools
    }
    print(f"[DEBUG] Request payload prepared: {request_payload}")

    try:
        # Call the OpenAI ChatCompletion API to get the assistant's response
        print("[DEBUG] Calling OpenAI ChatCompletion API")
        completion = client.chat.completions.create(
            model=model,
            messages=conversation_history,
            max_completion_tokens=750,
            functions=tools
        )
        print("[DEBUG] OpenAI API call successful")

        # Calculate latency in milliseconds
        end_time = datetime.utcnow()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        print(f"[DEBUG] Latency calculated: {latency_ms} ms")

        message = completion.choices[0].message
        assistant_response = message.content or ""
        print(f"[DEBUG] Assistant response: {assistant_response}")

        # Fix: Use attribute access instead of .get for ChatCompletionMessage
        if hasattr(message, "function_call") and message.function_call is not None:
            print("[DEBUG] Function call detected in response")
            function_call = message.function_call
            function_name = function_call.name
            function_args = json.loads(function_call.arguments)
            print(f"[DEBUG] Function call details: name={function_name}, arguments={function_args}")

            # Execute the appropriate tool function
            tool_result = None
            if function_name == "cfr_search":
                print("[DEBUG] Executing cfr_search tool")
                tool_result = search_cfr_documents(**function_args)
            elif function_name == "m21_search":
                print("[DEBUG] Executing m21_search tool")
                tool_result = search_m21_documents(**function_args)

            print(f"[DEBUG] Tool result: {tool_result}")

            # Append the tool result to the conversation history
            conversation_history.append({
                "role": "function",
                "name": function_name,
                "content": tool_result
            })

            # Re-call the API with the updated conversation history
            print("[DEBUG] Re-calling OpenAI API with updated conversation history")
            completion = client.chat.completions.create(
                model=model,
                messages=conversation_history,
                max_completion_tokens=750
            )
            assistant_response = completion.choices[0].message.content or ""

        # Append the assistant's response to the conversation history
        assistant_message = {
            "role": "assistant",
            "content": assistant_response
        }
        conversation_history.append(assistant_message)

        # Calculate token usage and cost
        token_usage = completion.usage
        cost_info = calculate_token_cost(
            prompt_tokens=token_usage.prompt_tokens,
            model=model,
            completion_tokens=token_usage.completion_tokens
        )
        print(f"[DEBUG] Token usage: {token_usage}, Cost info: {cost_info}")

        # Store OpenAI API log (success) and get log_id
        log = OpenAIAPILog(
            user_id=user_id,
            request_prompt=user_message,
            request_payload=request_payload,
            request_sent_at=start_time,
            response_json=completion.to_dict() if hasattr(completion, 'to_dict') else str(completion),
            response_received_at=end_time,
            status="success",
            error_message=None
        )
        ScopedSession.add(log)
        ScopedSession.commit()
        log_id = log.id
        print(f"[DEBUG] OpenAI API log stored with log_id: {log_id}")

        # Store analytics data with latency and log_id
        store_request_analytics(token_usage, cost_info, latency_ms=latency_ms, model=model, log_id=log_id)

        return {
            "chat_response": assistant_response,
            "conversation_history": conversation_history,
            "token_usage": {
                "prompt_tokens": token_usage.prompt_tokens,
                "completion_tokens": token_usage.completion_tokens,
                "total_tokens": token_usage.total_tokens
            },
            "cost": cost_info,
            "latency_ms": latency_ms
        }, 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        # Store OpenAI API log (error)
        end_time = datetime.utcnow()
        log = OpenAIAPILog(
            user_id=user_id,
            request_prompt=user_message,
            request_payload=request_payload,
            request_sent_at=start_time,
            response_json=None,
            response_received_at=end_time,
            status="error",
            error_message=str(e)
        )
        ScopedSession.add(log)
        ScopedSession.commit()
        log_id = log.id
        print(f"[DEBUG] Error log stored with log_id: {log_id}")

        # Store analytics data with error and log_id
        store_request_analytics(
            token_usage if 'token_usage' in locals() else {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
            cost_info if 'cost_info' in locals() else {'prompt_cost': 0, 'completion_cost': 0, 'total_cost': 0},
            latency_ms=(int((end_time - start_time).total_seconds() * 1000)),
            model=model,
            log_id=log_id
        )

        return {"error": str(e)}, 500