"""Generate embeddings in MongoDB and configure Atlas Vector Search indexes."""

import time
from pymongo.operations import SearchIndexModel, UpdateOne
from config import (
    get_mongo_db,
    get_embedding_model,
    EMBEDDING_DIMENSIONS,
    VENDOR_VECTOR_INDEX,
    CUSTOMER_VECTOR_INDEX,
)


def _embed_collection(collection, model) -> int:
    """Compute and store description_embedding on every document in a collection."""
    docs = list(collection.find({}, {"_id": 1, "description": 1}))
    if not docs:
        return 0

    descriptions = [d["description"] for d in docs]
    embeddings = model.encode(descriptions, normalize_embeddings=True).tolist()

    ops = [
        UpdateOne({"_id": d["_id"]}, {"$set": {"description_embedding": emb}})
        for d, emb in zip(docs, embeddings)
    ]
    collection.bulk_write(ops)
    return len(docs)


def _ensure_vector_index(collection, index_name: str, filter_fields: list[str]) -> None:
    """Create or update a MongoDB Atlas Vector Search index on description_embedding."""
    definition = {
        "fields": [
            {
                "type": "vector",
                "path": "description_embedding",
                "numDimensions": EMBEDDING_DIMENSIONS,
                "similarity": "cosine",
            },
            *[{"type": "filter", "path": f} for f in filter_fields],
        ]
    }

    existing = {idx["name"]: idx for idx in collection.list_search_indexes()}
    if index_name in existing:
        collection.update_search_index(name=index_name, definition=definition)
        print(f"Updated Atlas Vector Search index '{index_name}' on '{collection.name}'.")
    else:
        model = SearchIndexModel(
            definition=definition,
            name=index_name,
            type="vectorSearch",
        )
        collection.create_search_index(model=model)
        print(f"Created Atlas Vector Search index '{index_name}' on '{collection.name}'.")


def _wait_for_index_ready(collection, index_name: str, timeout_s: int = 90) -> bool:
    """Poll Atlas until the vector search index is READY / queryable."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        indexes = list(collection.list_search_indexes(name=index_name))
        if indexes:
            idx = indexes[0]
            status = idx.get("status", "UNKNOWN")
            queryable = idx.get("queryable", False)
            if queryable or status == "READY":
                print(f"Index '{index_name}' on '{collection.name}' is READY (queryable={queryable}).")
                return True
            print(f"Waiting for '{index_name}'... status={status}, queryable={queryable}")
        time.sleep(5)
    print(f"Timed out waiting for '{index_name}' to become READY; check Atlas UI if needed.")
    return False


def setup_vector_db():
    """Store embeddings in MongoDB and create Atlas Vector Search indexes."""
    db = get_mongo_db()
    model = get_embedding_model()

    vendor_col = db["vendor_catalog"]
    customer_col = db["customer_po_items"]

    v_count = _embed_collection(vendor_col, model)
    print(f"Stored 384-dim embeddings on {v_count} documents in '{db.name}.vendor_catalog'.")

    c_count = _embed_collection(customer_col, model)
    print(f"Stored 384-dim embeddings on {c_count} documents in '{db.name}.customer_po_items'.")

    _ensure_vector_index(vendor_col, VENDOR_VECTOR_INDEX, ["category", "vendor_id"])
    _ensure_vector_index(customer_col, CUSTOMER_VECTOR_INDEX, ["po_number", "customer_id"])

    _wait_for_index_ready(vendor_col, VENDOR_VECTOR_INDEX)
    _wait_for_index_ready(customer_col, CUSTOMER_VECTOR_INDEX)


if __name__ == "__main__":
    setup_vector_db()
