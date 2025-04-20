from datetime import datetime
from models.sql_models import AnalyticsData
from database.session import ScopedSession
from sqlalchemy import func

def get_analytics_summary():
    """Get summary of analytics data."""
    try:
        # Get total cost
        total_cost = ScopedSession.query(func.sum(AnalyticsData.total_cost)).scalar() or 0
        
        # Get total requests
        total_requests = ScopedSession.query(func.count(AnalyticsData.id)).scalar() or 0
        
        # Calculate average cost per request
        average_cost = total_cost / total_requests if total_requests > 0 else 0
        
        # Get total tokens
        total_sent_tokens = ScopedSession.query(func.sum(AnalyticsData.prompt_tokens)).scalar() or 0
        total_received_tokens = ScopedSession.query(func.sum(AnalyticsData.completion_tokens)).scalar() or 0
        
        # Get average latency
        average_latency = ScopedSession.query(func.avg(AnalyticsData.latency_ms)).scalar() or 0
        
        # Get recent requests
        recent_requests = ScopedSession.query(AnalyticsData).order_by(AnalyticsData.date.desc()).limit(10).all()
        
        # Format recent requests
        requests_by_date = [{
            "id": req.id,  # Include analytics row id
            "log_id": req.log_id,  # Include log_id for frontend use
            "date": req.date.strftime("%Y-%m-%d %H:%M:%S"),
            "model": req.model,
            "sentTokens": req.prompt_tokens,
            "receivedTokens": req.completion_tokens,
            "cost": float(req.total_cost),  # Convert to float explicitly
            "latency_ms": req.latency_ms
        } for req in recent_requests]
        
        # Get cost by model
        cost_by_model = {}
        model_costs = ScopedSession.query(
            AnalyticsData.model,
            func.sum(AnalyticsData.total_cost).label('total_cost')
        ).group_by(AnalyticsData.model).all()
        
        for model, cost in model_costs:
            cost_by_model[model] = float(cost)
        
        return {
            "totalCost": float(total_cost),
            "totalRequests": total_requests,
            "averageCostPerRequest": float(average_cost),
            "totalSentTokens": int(total_sent_tokens),
            "totalReceivedTokens": int(total_received_tokens),
            "averageLatency": float(average_latency),
            "requestsByDate": requests_by_date,
            "costByModel": cost_by_model
        }
    except Exception as e:
        print(f"Error getting analytics summary: {e}")
        return {
            "totalCost": 0,
            "totalRequests": 0,
            "averageCostPerRequest": 0,
            "totalSentTokens": 0,
            "totalReceivedTokens": 0,
            "averageLatency": 0,
            "requestsByDate": [],
            "costByModel": {}
        }