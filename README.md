# Purchase Order SKU Similarity & Mapping POC (MongoDB Atlas Vector Search)

A proof-of-concept showing how to match Customer Purchase Order line items to Vendor Catalog items using **MongoDB Atlas Vector Search** (`$vectorSearch` aggregation pipeline) on item descriptions, and persist Customer SKU ↔ Vendor SKU mappings in MongoDB.

## Architecture

1. **MongoDB Atlas (`purchase_order_poc` database)**
   - `vendor_catalog`: Vendor-side items with `line_item_id`, `sku`, `description`, `description_embedding` (384-dim vector), `vendor_id`, `vendor_name`, `uom`, and `unit_price`.
     - **Search Index**: `vendor_vector_index` (`type: "vectorSearch"`, cosine similarity on `description_embedding`).
   - `customer_purchase_orders`: Customer-side Purchase Orders with embedded `line_items`.
   - `customer_po_items`: Flattened customer PO line items with `description_embedding` (384-dim vector).
     - **Search Index**: `customer_vector_index` (`type: "vectorSearch"`, cosine similarity on `description_embedding`).
   - `sku_mappings`: Persisted mappings between `customer_sku` and `vendor_sku` (including `same_sku` flag, `similarity_score`, and both descriptions).

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env` (already configured; see `.env.example` for template).
3. Seed MongoDB with Customer POs and Vendor Catalog items:
   ```bash
   python seed_db.py
   ```
4. Generate embeddings in MongoDB and create the Atlas Vector Search indexes:
   ```bash
   python setup_vector_db.py
   ```

## Running the App (`app.py`)

### Interactive Mode
```bash
python app.py
```

### Search by Description ($vectorSearch) & Save Top Match
```bash
python app.py --desc "Isopropyl Alcohol 99% Pure Cleaning Solvent 1 Liter Bottle" --customer-sku "CUST-CHEM-IPA1L" --top-k 3 --save-top
```

### Auto-Match All Line Items in a Purchase Order
```bash
python app.py --po PO-2026-101 --save
```

### View Saved SKU Mappings
```bash
python app.py --list-mappings
```
