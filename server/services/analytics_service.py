# server/services/analytics_service.py

from datetime import datetime
from models.sql_models import AnalyticsData, OpenAIAPILog
from database.session import ScopedSession
from helpers.analytics_helpers import get_analytics_summary as get_summary_helper

def store_request_analytics(token_usage, cost_info, model="o3-mini-2025-01-31", latency_ms=0, log_id=None):
    """Store analytics data for a request."""
    try:
        # Check if token_usage is a dictionary or an object with attributes
        if hasattr(token_usage, 'prompt_tokens'):
            # It's an object with attributes
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
        else:
            # It's a dictionary
            prompt_tokens = token_usage["prompt_tokens"]
            completion_tokens = token_usage["completion_tokens"]
            total_tokens = token_usage["total_tokens"]
        
        analytics = AnalyticsData(
            date=datetime.utcnow(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            prompt_cost=cost_info["prompt_cost"],
            completion_cost=cost_info["completion_cost"],
            total_cost=cost_info["total_cost"],
            latency_ms=latency_ms,
            log_id=log_id  # <-- Add log_id to AnalyticsData
        )
        ScopedSession.add(analytics)
        ScopedSession.commit()
        
        # Get the updated analytics summary
        updated_analytics = get_summary_helper()
        
        return True, updated_analytics
    except Exception as e:
        print(f"Error storing analytics data: {e}")
        ScopedSession.rollback()
        return False, None

# The get_analytics_summary function has been moved to analytics_helpers.py
# This function is kept for backward compatibility
def get_analytics_summary():
    """Get summary of analytics data."""
    return get_summary_helper()

def store_openai_api_log(
    user_id=None,
    request_prompt=None,
    request_payload=None,
    request_sent_at=None,
    response_json=None,
    response_received_at=None,
    status=None,
    error_message=None
):
    """Store OpenAI API request/response log."""
    log = OpenAIAPILog(
        user_id=user_id,
        request_prompt=request_prompt,
        request_payload=request_payload,
        request_sent_at=request_sent_at or datetime.utcnow(),
        response_json=response_json,
        response_received_at=response_received_at or datetime.utcnow(),
        status=status,
        error_message=error_message
    )
    try:
        ScopedSession.add(log)
        ScopedSession.commit()
        return True
    except Exception as e:
        ScopedSession.rollback()
        print(f"Failed to store OpenAI API log: {e}")
        return False