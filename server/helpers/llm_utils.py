# server/helpers/llm_utils.py
# Functions Tools to interact with the OpenAI API

from database import db
from models.sql_models import MyTable
import json
import uuid
from openai import OpenAI
#from helpers.token_utils import calculate_token_cost
#from services.analytics_service import store_request_analytics
import os

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

model="o1-2024-12-17"

def fetch_something(filter_params: dict) -> list:
    """
    Query the table
        }
    :return: query object
    """
    query = db.session.query(MyTable)
    
    
    return query
