# analytics_routes.py

# Import necessary modules
import io
import csv
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from database.session import ScopedSession
from models.sql_models import AnalyticsData, OpenAIAPILog
from helpers.cors_helpers import pre_authorized_cors_preflight
from helpers.analytics_helpers import get_analytics_summary
from services.analytics_service import store_request_analytics

# Blueprint for analytics routes
analytics_bp = Blueprint("analytics", __name__)

# Define the analytics routes
@pre_authorized_cors_preflight
@analytics_bp.route("/analytics/store", methods=["POST"])
def store_analytics():
    """Store analytics data for a request."""
    try:
        data = request.get_json(force=True)
        print("DEBUG: Received analytics data:", data)

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Get the token usage and cost info
        token_usage = data.get("token_usage", {})
        cost_info = data.get("cost", {})
        if "model" not in data:
            raise ValueError("Missing required field: model")
        model = data["model"]
        
        # Store the analytics data
        success, updated_analytics = store_request_analytics(token_usage, cost_info, model)
        
        if success:
            return jsonify({
                "message": "Analytics data stored successfully",
                "analytics": updated_analytics
            }), 200
        else:
            return jsonify({"error": "Failed to store analytics data"}), 500

    except Exception as e:
        print("DEBUG: Exception encountered in store analytics:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Define the analytics summary route
@pre_authorized_cors_preflight
@analytics_bp.route("/analytics/summary", methods=["GET"])
def get_summary():
    """Get analytics summary."""
    try:
        # Get the analytics summary
        summary = get_analytics_summary()
        return jsonify(summary), 200

    except Exception as e:
        print("DEBUG: Exception encountered in get analytics summary:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Define the analytics reset route
@pre_authorized_cors_preflight
@analytics_bp.route("/analytics/reset", methods=["POST"])
def reset_analytics():
    """Reset all analytics data and OpenAI API logs."""
    try:
        # Delete all records from the analytics_data and openai_api_logs tables
        ScopedSession.query(AnalyticsData).delete()
        ScopedSession.query(OpenAIAPILog).delete()
        ScopedSession.commit()
        
        # Get the updated analytics summary (should be empty)
        updated_analytics = get_analytics_summary()
        
        return jsonify({
            "message": "Analytics data and OpenAI API logs reset successfully",
            "analytics": updated_analytics
        }), 200
    except Exception as e:
        print("DEBUG: Exception encountered in reset analytics:", e)
        import traceback
        traceback.print_exc()
        ScopedSession.rollback()
        return jsonify({"error": str(e)}), 500

# Define the OpenAI log route
@pre_authorized_cors_preflight
@analytics_bp.route("/analytics/openai-log/<int:log_id>", methods=["GET"])
def get_openai_log(log_id):
    """Fetch the OpenAI API log for a given log_id."""
    try:
        log = ScopedSession.query(OpenAIAPILog).filter_by(id=log_id).first()
        if not log:
            return jsonify({"error": "OpenAI log not found"}), 404
        # Serialize the log fields
        log_data = {
            "id": log.id,
            "user_id": log.user_id,
            "request_prompt": log.request_prompt,
            "request_payload": log.request_payload,
            "request_sent_at": log.request_sent_at.isoformat() if log.request_sent_at else None,
            "response_json": log.response_json,
            "response_received_at": log.response_received_at.isoformat() if log.response_received_at else None,
            "status": log.status,
            "error_message": log.error_message,
        }
        return jsonify(log_data), 200
    except Exception as e:
        print(f"Error fetching OpenAI log: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
# Define the analytics download route
@pre_authorized_cors_preflight
@analytics_bp.route("/analytics/download", methods=["GET"])
def download_report():
    """Generate and download analytics report."""
    try:
        # Get all analytics data
        analytics_data = ScopedSession.query(AnalyticsData).order_by(AnalyticsData.date.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date',
            'Model',
            'Prompt Tokens',
            'Completion Tokens',
            'Total Tokens',
            'Prompt Cost',
            'Completion Cost',
            'Total Cost'
        ])
        
        # Write data
        for record in analytics_data:
            writer.writerow([
                record.date.strftime("%Y-%m-%d %H:%M:%S"),
                record.model,
                record.prompt_tokens,
                record.completion_tokens,
                record.total_tokens,
                float(record.prompt_cost),
                float(record.completion_cost),
                float(record.total_cost)
            ])
        
        # Prepare the response
        output.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'analytics_report_{timestamp}.csv'
        )

    except Exception as e:
        print("DEBUG: Exception encountered in download report:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500