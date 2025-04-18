# server/services/chat_service.py

import os
import json
from openai import OpenAI
from datetime import datetime
import pytz
from helpers.token_utils import calculate_token_cost
from services.analytics_service import store_request_analytics, store_openai_api_log
from models.sql_models import OpenAIAPILog
from database.session import ScopedSession

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# This is the model that we are using for the chat service
model="gpt-4.1-nano-2025-04-14"

def get_system_message():
    """Return the system message for the chat."""
    return {
        "role": "system",
        "content": (
            """ 
            You are a helpful assistant.
            """
        )
    }

def get_time_context_message():
    """Get the current time in EST and return a time context message."""
    try:
        # Get current time in EST using a reliable method
        est = pytz.timezone('US/Eastern')
        current_time = datetime.now(est)
        current_time_formatted = current_time.strftime('%Y-%m-%d %H:%M:%S EST')
    except Exception as e:
        # Fallback to a simpler approach
        from datetime import datetime, timedelta
        # EST is UTC-5
        utc_now = datetime.utcnow()
        est_offset = timedelta(hours=-5)
        est_time = utc_now + est_offset
        current_time_formatted = est_time.strftime('%Y-%m-%d %H:%M:%S EST')
    
    return {
        "role": "system",
        "content": f"Current time: {current_time_formatted}"
    }

def process_chat(user_message, conversation_history, user_id=None):
    """Process a chat message and return the response."""
    if not user_message:
        return {"error": "No 'message' provided"}, 400
    # Ensure conversation_history is a list
    if not isinstance(conversation_history, list):
        conversation_history = []
    # Check if the conversation history already has a system message
    has_system_message = any(msg.get("role") == "system" and "You are a helpful assistant" in msg.get("content", "") for msg in conversation_history)
    # If no conversation history or no system message, add the system message
    if not conversation_history or not has_system_message:
        conversation_history.insert(0, get_system_message())
    # Check if there's a time context message in the conversation history
    has_time_context = any(msg.get("role") == "system" and "Current time:" in msg.get("content", "") for msg in conversation_history)
    # If no time context message, add one
    if not has_time_context:
        conversation_history.append(get_time_context_message())
    # Record start time for latency tracking
    start_time = datetime.utcnow()
    request_payload = {
        "model": model,
        "messages": conversation_history,
        "max_completion_tokens": 750
    }
    try:
        # Call ChatCompletion API
        completion = client.chat.completions.create(
            model=model,
            messages=conversation_history,
            max_completion_tokens=750
        )
        # Calculate latency in milliseconds
        end_time = datetime.utcnow()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        message = completion.choices[0].message
        # Calculate token usage and cost
        token_usage = completion.usage
        cost_info = calculate_token_cost(
            prompt_tokens=token_usage.prompt_tokens,
            model=model,
            completion_tokens=token_usage.completion_tokens
        )
        assistant_response = message.content or ""
        assistant_message = {
            "role": "assistant",
            "content": assistant_response
        }
        conversation_history.append(assistant_message)

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
        # Store analytics data with error and log_id
        store_request_analytics(token_usage if 'token_usage' in locals() else {'prompt_tokens':0,'completion_tokens':0,'total_tokens':0},
                               cost_info if 'cost_info' in locals() else {'prompt_cost':0,'completion_cost':0,'total_cost':0},
                               latency_ms=(int((end_time - start_time).total_seconds() * 1000)),
                               model=model,
                               log_id=log_id)
        return {"error": str(e)}, 500