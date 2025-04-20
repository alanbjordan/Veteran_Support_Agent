# llm_wrappers.py

# Import necessary modules
import os
from openai import OpenAI
from datetime import datetime
from database.session import ScopedSession

# Ensure the OpenAI API key is set
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Function to get embeddings using OpenAI API
def call_openai_embeddings(
    input_text: str,
    model: str,
    **kwargs
):
    """Get embeddings from OpenAI API."""
    # 1) Get the OpenAI API key from environment variables
    if not api_key:
        raise ValueError("OpenAI API key is not set.")

    # 2) Call the OpenAI API to get embeddings
    response = client.embeddings.create(
            input=input_text,
            model=model,
            **kwargs
        )

    # 3) Process the response and return the embeddings
    if response and "data" in response:
        return response["data"][0]["embedding"]
    
    raise ValueError("Failed to get embeddings from OpenAI API.")
