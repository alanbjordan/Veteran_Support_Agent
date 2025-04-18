# helpers/chatbot_helper.py

import os
import json
import requests
import concurrent.futures
import time
import traceback  # For printing errors
from flask import g
from openai import OpenAI
from pinecone import Pinecone
import decimal
from helpers.llm_wrappers import call_openai_chat_create, call_openai_embeddings

# Import both Conditions and ConditionEmbedding so we can do the basic list + semantic search
from models.legacy_sql_models import Conditions, ConditionEmbedding, NexusTags, Tag

###############################################################################
# 1. ENV & GLOBAL SETUP
###############################################################################

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"  # or whichever region you use

INDEX_NAME_CFR = "38-cfr-index"
INDEX_NAME_M21 = "m21-index"

# Two different embedding models:
# - The "small" one for Pinecone (1536 dims)
# - The "large" one for Postgres pgvector (3072 dims)
EMBEDDING_MODEL_SMALL = "text-embedding-3-small"
EMBEDDING_MODEL_LARGE = "text-embedding-3-large"

# Initialize the OpenAI client
client = OpenAI()

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index_cfr = pc.Index(INDEX_NAME_CFR)
index_m21 = pc.Index(INDEX_NAME_M21)

PART_3_URL = "/home/jsnow/ML-project/Agent_testing/Veteran_Claims_Agent/server/json/part_3_flattened.json"
PART_4_URL = "/home/jsnow/ML-project/Agent_testing/Veteran_Claims_Agent/server/json/part_4_flattened.json"
M21_1_URL = "/home/jsnow/ML-project/Agent_testing/Veteran_Claims_Agent/server/json/m21_1_chunked3k.json"
M21_5_URL = "/home/jsnow/ML-project/Agent_testing/Veteran_Claims_Agent/server/json/m21_5_chunked3k.json"

###############################################################################
# 2. QUERY CLEANUP
###############################################################################
def clean_up_query_with_llm(user_query: str) -> str:
    """
    Uses an OpenAI LLM to rewrite the user query in a more standardized,
    formal, or clarified way—removing slang, expanding contractions, etc.
    Now directly calls the OpenAI API without any wrappers.
    """
    system_message = (
        """
        # Identity
        *You are a helpful assistant that rewrites user queries for better text embeddings. 

        # Instructions
        * Expand or remove contractions, fix grammatical errors, and keep the original meaning. 
        * Be concise and ensure the question is still natural and complete. You will rewrite it 
        professionally as if talking directly to a VA rater who could answer the question. 
        * Remove sentences not relevant to the question.
        """
        
    )

    # Create messages for the API call
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_query}
    ]

    # Directly call the OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",  # Use the same model as in chat_service.py
        messages=messages,
        max_completion_tokens=750
    )
    
    # Extract the cleaned query from the response
    cleaned_query = completion.choices[0].message.content
    return cleaned_query.strip()



###############################################################################
# 3. EMBEDDING FUNCTIONS
###############################################################################
def get_embedding_small(user_id: int, text: str) -> list:
    # $0.020 per 1M => 0.00000002 per token
    cost_rate = decimal.Decimal("0.00000002")
    response = call_openai_embeddings(
        user_id=user_id,
        input_text=text,
        model="text-embedding-3-small",
        cost_per_token=cost_rate
    )
    return response.data[0].embedding

def get_embedding_large(user_id: int, text: str) -> list:
    # $0.130 per 1M => 0.00000013 per token
    cost_rate = decimal.Decimal("0.00000013")
    response = call_openai_embeddings(
        user_id=user_id,
        input_text=text,
        model="text-embedding-3-large",
        cost_per_token=cost_rate
    )
    return response.data[0].embedding

###############################################################################
# 4. MULTITHREADED SECTION RETRIEVAL FOR CFR / M21
###############################################################################
def fetch_matches_content(search_results, max_workers=3) -> list:
    """
    Fetch section text for all Pinecone matches (38 CFR) from remote JSON files on the server'.
    """
    matches = search_results.get("matches", [])

    def get_section_text(section_number: str, part_number: str) -> str:
        # 1) Decide which URL to request
        if part_number == "3":
            url = PART_3_URL
        elif part_number == "4":
            url = PART_4_URL
        else:
            return None

        # 2) Fetch and parse the JSON data from Azure
        try:
            resp = requests.get(url)
            resp.raise_for_status()  # will raise an exception if 4xx/5xx
            data = resp.json()
        except Exception as e:
            print(f"[ERROR] Unable to fetch or parse JSON from {url}: {e}")
            return None

        # 3) Search for the matching section_number
        for item in data:
            meta = item.get("metadata", {})
            if meta.get("section_number") == section_number:
                return item.get("text")
        return None

    matching_texts = []
    for match in matches:
        metadata = match.get("metadata", {})
        section_num = metadata.get("section_number")
        part_number = metadata.get("part_number")
        if not section_num or not part_number:
            continue

        # fetch the matching text from Azure
        section_text = get_section_text(section_num, part_number)
        matching_texts.append({
            "section_number": section_num,
            "matching_text": section_text
        })

    return matching_texts


def fetch_matches_content_m21(search_results, max_workers=3) -> list:
    """
    Fetch article text for all Pinecone matches (M21) from remote JSON files in the server.
    Returns a list of dicts with 'article_number' and 'matching_text'.
    """
    matches = search_results.get("matches", [])

    def get_article_text(article_number: str, manual: str) -> str:
        # Determine which URL to download based on manual
        if manual == "M21-1":
            url = M21_1_URL
        elif manual == "M21-5":
            url = M21_5_URL
        else:
            return None

        # Fetch and parse the JSON data from Azure
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[ERROR] Unable to fetch or parse JSON from {url}: {e}")
            return None

        # Search for the matching article_number
        for item in data:
            meta = item.get("metadata", {})
            if meta.get("article_number") == article_number:
                return item.get("text")
        return None

    matching_texts = []
    for match in matches:
        metadata = match.get("metadata", {})
        article_num = metadata.get("article_number")
        manual_val = metadata.get("manual")
        if not article_num or not manual_val:
            continue

        article_text = get_article_text(article_num, manual_val)
        matching_texts.append({
            "article_number": article_num,
            "matching_text": article_text
        })

    return matching_texts


###############################################################################
# 5. PINECONE SEARCH FUNCTIONS (CFR and M21) - using the SMALL model
###############################################################################
def search_cfr_documents(user_id, query: str, top_k: int = 3) -> str:
    cleaned_query = clean_up_query_with_llm(user_id, query)
    query_emb = get_embedding_small(user_id, cleaned_query)

    results = index_cfr.query(
        vector=query_emb,
        top_k=top_k,
        include_metadata=True
    )

    matching_sections = fetch_matches_content(results, max_workers=3)
    if not matching_sections:
        return "No sections found (CFR)."

    references_str = ""
    for item in matching_sections:
        sec_num = item["section_number"]
        text_snippet = item["matching_text"] or "N/A"
        references_str += f"\n---\nSection {sec_num}:\n{text_snippet}\n"
    print(references_str)

    return references_str.strip()


def search_m21_documents(user_id, query: str, top_k: int = 3) -> str:
    cleaned_query = clean_up_query_with_llm(user_id, query)
    query_emb = get_embedding_small(user_id, cleaned_query)

    results = index_m21.query(
        vector=query_emb,
        top_k=top_k,
        include_metadata=True
    )
    matching_articles = fetch_matches_content_m21(results, max_workers=3)
    if not matching_articles:
        return "No articles found (M21)."

    references_str = ""
    for item in matching_articles:
        article_num = item["article_number"]
        text_snippet = item["matching_text"] or "N/A"
        references_str += f"\n---\nArticle {article_num}:\n{text_snippet}\n"
    print(references_str)
    return references_str.strip()
