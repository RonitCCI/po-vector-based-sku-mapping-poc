# Documentation Index — Purchase Order SKU Similarity & Mapping POC

Welcome to the documentation for the **Purchase Order SKU Similarity & Mapping POC**, powered by **MongoDB Atlas Vector Search** (`$vectorSearch`) and `all-MiniLM-L6-v2` embeddings.

## Documents

1. **[Architecture & Query Lifecycle](ARCHITECTURE.md)**
   - End-to-end system diagram, ingestion vs. query flows, and MongoDB Atlas `$vectorSearch` sequence.
2. **[Database Representation & Schema](DATABASE_SCHEMA.md)**
   - Entity-Relationship diagram (`vendor_catalog`, `customer_purchase_orders`, `customer_po_items`, `sku_mappings`), Atlas Vector Search index definitions, and sample documents.
3. **[The Math Behind Embeddings, Cosine Similarity & SKU Mapping](MATH_AND_MAPPING.md)**
   - L2-normalized dense embeddings, Cosine Similarity, MongoDB `vectorSearchScore`, HNSW approximate nearest neighbors, and Same-SKU vs. Cross-SKU mapping logic.
4. **[Live Demo Presenter Script](DEMO_SCRIPT.md)**
   - Step-by-step walkthrough for presenting the POC in the Web UI (`http://127.0.0.1:5000`) and terminal (`python demo.py`).
