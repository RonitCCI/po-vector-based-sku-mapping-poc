"""Shared configuration and MongoDB/embedding helpers for the Purchase Order SKU Mapping POC."""

import os
from functools import lru_cache
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "purchase_order_poc")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSIONS = 384

VENDOR_VECTOR_INDEX = "vendor_vector_index"
CUSTOMER_VECTOR_INDEX = "customer_vector_index"


def get_mongo_db():
    """Return a connected MongoDB database instance."""
    if not MONGO_URI:
        raise ValueError("MONGO_URI is not set. Check your .env file.")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    return client[MONGO_DB_NAME]


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load and cache the SentenceTransformer embedding model."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL)
