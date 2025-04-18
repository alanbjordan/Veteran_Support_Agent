# This file defines the SQLAlchemy models for the car inventory system.
# server/models/sql_models.py
from datetime import datetime
from database import db  

# Model for storing full OpenAI API request/response logs
class OpenAIAPILog(db.Model):
    __tablename__ = "openai_api_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # Optional: reference to user/session
    request_prompt = db.Column(db.Text, nullable=True)  # The prompt sent to OpenAI
    request_payload = db.Column(db.JSON, nullable=True)  # The full request payload (if applicable)
    request_sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # When the request was sent
    response_json = db.Column(db.JSON, nullable=False)  # The full OpenAI API response
    response_received_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # When the response was received
    status = db.Column(db.String(50), nullable=True)  # e.g., 'success', 'error'
    error_message = db.Column(db.Text, nullable=True)  # Optional: error details if any

    def __repr__(self):
        return f"<OpenAIAPILog {self.id} - {self.status} {self.request_sent_at}>"

# Define the AnalyticsData model
class AnalyticsData(db.Model):
    __tablename__ = "analytics_data"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    prompt_tokens = db.Column(db.Integer, nullable=False)
    completion_tokens = db.Column(db.Integer, nullable=False)
    total_tokens = db.Column(db.Integer, nullable=False)
    prompt_cost = db.Column(db.Numeric(10, 7), nullable=False)
    completion_cost = db.Column(db.Numeric(10, 7), nullable=False)
    total_cost = db.Column(db.Numeric(10, 7), nullable=False)
    latency_ms = db.Column(db.Integer, nullable=False)  # Latency in milliseconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AnalyticsData {self.date} - {self.model}>"