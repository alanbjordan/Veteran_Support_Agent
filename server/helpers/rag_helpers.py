# server/helpers/rag_helpers.py

# Import necessary libraries
import os
import json
import decimal
import requests
from flask import g
from database import db
from openai import OpenAI
from pinecone import Pinecone

###############################################################################
# 1. ENV & GLOBAL SETUP
###############################################################################

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"

INDEX_NAME_CFR = "38-cfr-index"
INDEX_NAME_M21 = "m21-index"

# Embedding model:
# - The "small" one for Pinecone (1536 dims)
EMBEDDING_MODEL_SMALL = "text-embedding-3-small"

# Initialize the OpenAI client
client = OpenAI()

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
# Initialize the Pinecone indexes
index_cfr = pc.Index(INDEX_NAME_CFR)
index_m21 = pc.Index(INDEX_NAME_M21)

# Load the JSON files
PART_3_URL = "./server/json/part_3_flattened.json"
PART_4_URL = "./server/json/part_4_flattened.json"
M21_1_URL = "./server/json/m21_1_chunked3k.json"
M21_5_URL = "./server/json/m21_5_chunked3k.json"

###############################################################################
# 2. QUERY CLEANUP
###############################################################################

# Function to transform the user query
def transform_query(user_query: str) -> str:
    """
    Uses an OpenAI LLM to rewrite the user query into a formal, structured inquiry that is 
    optimized for semantic search on 38 CFR or the M21 Manual of VA Regulations. The LLM will 
    expand contractions, fix grammatical errors, remove irrelevant sentences, and create a query 
    suitable for text embeddings.
    """
    system_message = (
        """
        # Identity
        You are a helpful assistant skilled at transforming user queries into clear, formal statements.

        # Instructions
        Given the user's query, rewrite it to formulate a precise, professional statement optimized 
        for semantic search across regulatory texts such as 38 CFR and the M21 Manual of VA Regulations. 
        Expand contractions, correct any grammatical errors, and remove any extraneous or unrelated 
        content. The final inquiry should be succinct, clear, and maintain the original intent while 
        aligning with legal and regulatory terminology.
        """
    )

    # Create messages for the API call
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_query}
    ]

    # Directly call the OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_completion_tokens=750,
        temperature=0.0
    )
    
    # Extract the cleaned query from the response
    cleaned_query = completion.choices[0].message.content
    return cleaned_query.strip()

###############################################################################
# 3. EMBEDDING FUNCTIONS
###############################################################################

# Function to get the embedding for a given text
def get_embedding_small(model, text: str) -> list:

    """
    Fetches the embedding for the given text using a smaller model or large model.
    """
    response = client.embeddings.create(
        input=text,
        model=model
        )
    return response.data[0].embedding

###############################################################################
# 4. MULTITHREADED SECTION RETRIEVAL FOR CFR / M21
###############################################################################

# Function to fetch matched content from Pinecone for 38 CFR
def fetch_matches_content(search_results) -> list:
    """
    Fetch section text for all Pinecone matches (38 CFR) from local JSON files.
    """
    matches = search_results.get("matches", [])

    def get_section_text(section_number: str, part_number: str) -> str:
        # Determine which local file to load based on the part number
        if part_number == "3":
            file_path = PART_3_URL
        elif part_number == "4":
            file_path = PART_4_URL
        else:
            return None
        
        # Open and load JSON data from the local file
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Unable to open or parse JSON from {file_path}: {e}")
            return None

        # Search for the matching section_number in the JSON data
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

        section_text = get_section_text(section_num, part_number)
        matching_texts.append({
            "section_number": section_num,
            "matching_text": section_text
        })

    return matching_texts

# Function to fetch matched content from Pinecone for M21
def fetch_matches_content_m21(search_results) -> list:
    """
    Fetch article text for all Pinecone matches (M21) from remote JSON files in the server.
    Returns a list of dicts with 'article_number' and 'matching_text'.
    """
    matches = search_results.get("matches", [])

    def get_article_text(article_number: str, manual: str) -> str:
        # Determine which URL to download based on manual
        if manual == "M21-1":
            file_path = M21_1_URL
        elif manual == "M21-5":
            file_path = M21_5_URL
        else:
            return None

        # Open and load JSON data from the local file
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Unable to open or parse JSON from {file_path}: {e}")
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
# 5. PINECONE SEARCH FUNCTIONS (CFR and M21)
###############################################################################

# Function to search for documents in the CFR indexes
def search_cfr_documents(query: str, top_k: int = 3) -> str:
    cleaned_query = transform_query(query)
    query_emb = get_embedding_small(EMBEDDING_MODEL_SMALL,cleaned_query)

    results = index_cfr.query(
        vector=query_emb,
        top_k=top_k,
        include_metadata=True
    )

    matching_sections = fetch_matches_content(results)
    if not matching_sections:
        return "No sections found (CFR)."

    references_str = ""
    for item in matching_sections:
        sec_num = item["section_number"]
        text_snippet = item["matching_text"] or "N/A"
        references_str += f"\n---\nSection {sec_num}:\n{text_snippet}\n"
    print(references_str)

    return references_str.strip()

# Function to search for documents in the M21 indexes
def search_m21_documents(query: str, top_k: int = 3) -> str:
    cleaned_query = transform_query(query)
    query_emb = get_embedding_small(EMBEDDING_MODEL_SMALL,cleaned_query)

    results = index_m21.query(
        vector=query_emb,
        top_k=top_k,
        include_metadata=True
    )
    matching_articles = fetch_matches_content_m21(results)
    if not matching_articles:
        return "No articles found (M21)."

    references_str = ""
    for item in matching_articles:
        article_num = item["article_number"]
        text_snippet = item["matching_text"] or "N/A"
        references_str += f"\n---\nArticle {article_num}:\n{text_snippet}\n"
    print(references_str)
    return references_str.strip()