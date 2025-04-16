# This file defines the SQLAlchemy models for the car inventory system.
# server/models/sql_models.py
from datetime import datetime
from database import db  

# Define the Data model
class MyTable(db.Model):
    __tablename__ = "my_table"

    id = db.Column(db.Integer, primary_key=True)
    column1 = db.Column(db.String(50), unique=True, nullable=False)
    column2 = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Data {self.column1} - {self.column2} {self.created_at}>"

# Define the AnalyticsData model
class AnalyticsData(db.Model):
    __tablename__ = "analytics_data"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    prompt_tokens = db.Column(db.Integer, nullable=False)
    completion_tokens = db.Column(db.Integer, nullable=False)
    total_tokens = db.Column(db.Integer, nullable=False)
    prompt_cost = db.Column(db.Numeric(10, 6), nullable=False)
    completion_cost = db.Column(db.Numeric(10, 6), nullable=False)
    total_cost = db.Column(db.Numeric(10, 6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AnalyticsData {self.date} - {self.model}>"