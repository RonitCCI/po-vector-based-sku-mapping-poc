# System Architecture & Data Flow

## High-Level Architecture

The POC uses **MongoDB Atlas** as both the operational document store and the vector search engine, eliminating the need for a separate vector database.

```mermaid
flowchart LR
    subgraph Ingestion["1. Seeding & Vector Indexing"]
        S["seed_db.py"] -->|"40 Vendor Items<br/>6 POs / 24 Line Items"| MDB[("MongoDB Atlas<br/>purchase_order_poc")]
        V["setup_vector_db.py"] -->|"Read descriptions"| MDB
        V -->|"Encode with<br/>all-MiniLM-L6-v2"| EMB["384-dim Unit Vectors"]
        EMB -->|"$set description_embedding<br/>+ create_search_index"| MDB
    end

    subgraph Runtime["2. Similarity Search & Mapping"]
        UI["Flask Web UI<br/>(web_app.py)"] --> APP["app.py<br/>search_similar_items()"]
        CLI["CLI / Demo<br/>(app.py / demo.py)"] --> APP
        APP -->|"1. Encode query desc"| EMB2["Query Vector (384-dim)"]
        EMB2 -->|"2. $vectorSearch<br/>aggregation pipeline"| MDB
        MDB -->|"3. Top-K ranked<br/>SKUs + scores"| APP
        APP -->|"4. Upsert confirmed<br/>SKU mapping"| MAP[("sku_mappings<br/>collection")]
    end
```

## `$vectorSearch` Query Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Web UI / CLI)
    participant App as Flask / app.py
    participant Model as SentenceTransformer<br/>(all-MiniLM-L6-v2)
    participant Atlas as MongoDB Atlas<br/>(vendor_catalog + vendor_vector_index)
    participant MapCol as MongoDB Atlas<br/>(sku_mappings)

    User->>App: Submit description (e.g. "Heavy Duty Nitrile Gloves Large...")
    App->>Model: encode([description], normalize_embeddings=True)
    Model-->>App: 384-dim L2-normalized vector q
    App->>Atlas: aggregate([$vectorSearch, $addFields(score), $project])
    Note over Atlas: HNSW index traverses cosine<br/>neighbors (numCandidates=50, limit=K)
    Atlas-->>App: Top-K vendor docs with vectorSearchScore
    App-->>User: Ranked Vendor SKUs + Similarity Scores
    User->>App: Confirm mapping (Customer SKU ↔ Vendor SKU)
    App->>MapCol: update_one(..., upsert=True)
    MapCol-->>User: Persisted mapping document
```

## Components

| Component | File | Responsibility |
| :--- | :--- | :--- |
| Config & Clients | [`config.py`](../config.py) | Loads `.env`, provides `get_mongo_db()` and cached `get_embedding_model()`. |
| Data Seeder | [`seed_db.py`](../seed_db.py) | Seeds `vendor_catalog`, `customer_purchase_orders`, `customer_po_items`, and indexes `sku_mappings`. |
| Vector Setup | [`setup_vector_db.py`](../setup_vector_db.py) | Computes `description_embedding` on all items and builds `vendor_vector_index` & `customer_vector_index`. |
| Core Engine & CLI | [`app.py`](../app.py) | Runs `$vectorSearch` pipelines, batch PO matching, and saves mappings to `sku_mappings`. |
| Web UI & API | [`web_app.py`](../web_app.py) | Serves the 4-tab demo UI at `http://127.0.0.1:5000` and REST endpoints. |
| Terminal Demo | [`demo.py`](../demo.py) | Guided step-by-step terminal presentation script. |
