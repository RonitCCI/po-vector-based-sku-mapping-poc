"""Flask Web UI & API for the Purchase Order SKU Similarity & Mapping POC."""

from flask import Flask, jsonify, render_template, request
from config import (
    get_mongo_db,
    get_embedding_model,
    VENDOR_VECTOR_INDEX,
    CUSTOMER_VECTOR_INDEX,
)
from app import search_similar_items, save_sku_mapping

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main testing & demo UI."""
    return render_template("index.html")


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Return live database and mapping statistics for the Overview dashboard."""
    db = get_mongo_db()
    vendor_count = db["vendor_catalog"].count_documents({})
    po_count = db["customer_purchase_orders"].count_documents({})
    cli_count = db["customer_po_items"].count_documents({})
    mappings = list(db["sku_mappings"].find({}, {"_id": 0, "same_sku": 1, "similarity_score": 1}))

    same_sku_count = sum(1 for m in mappings if m.get("same_sku"))
    diff_sku_count = len(mappings) - same_sku_count
    avg_score = (
        round(sum(float(m.get("similarity_score", 0.0)) for m in mappings) / len(mappings), 4)
        if mappings
        else 0.0
    )
    categories = sorted(db["vendor_catalog"].distinct("category"))

    return jsonify(
        {
            "vendor_items": vendor_count,
            "purchase_orders": po_count,
            "customer_line_items": cli_count,
            "total_mappings": len(mappings),
            "same_sku_mappings": same_sku_count,
            "cross_sku_mappings": diff_sku_count,
            "avg_similarity_score": avg_score,
            "categories": categories,
        }
    )


@app.route("/api/pos", methods=["GET"])
def get_pos():
    """Return all Customer Purchase Orders from MongoDB."""
    db = get_mongo_db()
    pos = list(db["customer_purchase_orders"].find({}, {"_id": 0}).sort("po_number", 1))
    return jsonify({"purchase_orders": pos})


@app.route("/api/vendor-catalog", methods=["GET"])
def get_vendor_catalog():
    """Return all Vendor Catalog items (without raw embedding vectors)."""
    db = get_mongo_db()
    items = list(
        db["vendor_catalog"]
        .find({}, {"_id": 0, "description_embedding": 0})
        .sort("line_item_id", 1)
    )
    return jsonify({"items": items})


@app.route("/api/search", methods=["POST"])
def api_search():
    """Run MongoDB Atlas $vectorSearch and return matches plus pipeline/vector preview."""
    data = request.get_json(silent=True) or {}
    description = (data.get("description") or "").strip()
    if not description:
        return jsonify({"error": "Description is required."}), 400

    target = data.get("target", "vendor")
    if target not in ("vendor", "customer"):
        target = "vendor"

    try:
        top_k = max(1, min(int(data.get("top_k", 5)), 20))
    except (TypeError, ValueError):
        top_k = 5

    category = (data.get("category") or "").strip()
    vector_filter = {"category": category} if (target == "vendor" and category) else None

    matches = search_similar_items(
        description=description,
        target=target,
        top_k=top_k,
        vector_filter=vector_filter,
    )

    # Build a preview of the query vector and aggregation pipeline for demo transparency
    model = get_embedding_model()
    query_vec = model.encode([description], normalize_embeddings=True)[0].tolist()
    index_name = VENDOR_VECTOR_INDEX if target == "vendor" else CUSTOMER_VECTOR_INDEX
    vs_stage = {
        "index": index_name,
        "path": "description_embedding",
        "queryVector": f"<384-dim float vector: [{', '.join(f'{v:.4f}' for v in query_vec[:4])}, ...]>",
        "numCandidates": max(top_k * 10, 50),
        "limit": top_k,
    }
    if vector_filter:
        vs_stage["filter"] = vector_filter

    pipeline_preview = [
        {"$vectorSearch": vs_stage},
        {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
        {"$project": {"_id": 0, "description_embedding": 0}},
    ]

    return jsonify(
        {
            "matches": matches,
            "target": target,
            "query": description,
            "query_vector_preview": [round(v, 5) for v in query_vec[:8]],
            "pipeline_preview": pipeline_preview,
        }
    )


@app.route("/api/mappings", methods=["GET"])
def get_mappings():
    """Return all saved SKU mappings from MongoDB."""
    db = get_mongo_db()
    mappings = list(db["sku_mappings"].find({}, {"_id": 0}).sort("updated_at", -1))
    for m in mappings:
        if m.get("updated_at"):
            m["updated_at"] = m["updated_at"].isoformat()
        if m.get("created_at"):
            m["created_at"] = m["created_at"].isoformat()
    return jsonify({"mappings": mappings})


@app.route("/api/mappings", methods=["POST"])
def create_mapping():
    """Save or update a Customer SKU <-> Vendor SKU mapping in MongoDB."""
    data = request.get_json(silent=True) or {}
    customer_sku = (data.get("customer_sku") or "").strip()
    vendor_sku = (data.get("vendor_sku") or "").strip()
    customer_description = (data.get("customer_description") or "").strip()
    vendor_description = (data.get("vendor_description") or "").strip()

    if not customer_sku or not vendor_sku:
        return jsonify({"error": "Both customer_sku and vendor_sku are required."}), 400

    saved = save_sku_mapping(
        customer_sku=customer_sku,
        vendor_sku=vendor_sku,
        customer_description=customer_description,
        vendor_description=vendor_description,
        similarity_score=float(data.get("similarity_score", 0.0)),
        po_number=data.get("po_number"),
        line_item_id=data.get("line_item_id"),
    )
    saved["updated_at"] = saved["updated_at"].isoformat()
    return jsonify({"mapping": saved})


@app.route("/api/mappings", methods=["DELETE"])
def delete_mapping():
    """Delete a saved SKU mapping by customer_sku and vendor_sku."""
    data = request.get_json(silent=True) or {}
    customer_sku = (data.get("customer_sku") or "").strip()
    vendor_sku = (data.get("vendor_sku") or "").strip()
    if not customer_sku or not vendor_sku:
        return jsonify({"error": "customer_sku and vendor_sku are required."}), 400

    db = get_mongo_db()
    res = db["sku_mappings"].delete_one({"customer_sku": customer_sku, "vendor_sku": vendor_sku})
    return jsonify({"deleted": res.deleted_count})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
