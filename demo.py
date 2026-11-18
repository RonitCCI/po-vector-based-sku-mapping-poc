"""Guided terminal demo script for the Purchase Order SKU Similarity & Mapping POC."""

import argparse
import json
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from config import get_mongo_db, get_embedding_model, VENDOR_VECTOR_INDEX
from app import search_similar_items, render_matches, map_purchase_order

console = Console()


def pause(fast: bool) -> None:
    if not fast:
        console.input("\n[dim]Press Enter to continue to the next demo step...[/dim]")


def run_demo(fast: bool = False) -> None:
    db = get_mongo_db()
    model = get_embedding_model()

    # Step 1: Database Overview
    console.print(
        Panel.fit(
            "[bold cyan]Step 1: MongoDB Atlas Data Overview (Both Ends)[/bold cyan]\n"
            f"Database: [yellow]{db.name}[/yellow]\n"
            f"• vendor_catalog: [green]{db['vendor_catalog'].count_documents({})}[/green] items\n"
            f"• customer_purchase_orders: [green]{db['customer_purchase_orders'].count_documents({})}[/green] POs\n"
            f"• customer_po_items: [green]{db['customer_po_items'].count_documents({})}[/green] line items\n"
            f"• sku_mappings: [green]{db['sku_mappings'].count_documents({})}[/green] saved mappings",
            title="Purchase Order SKU Mapping POC",
        )
    )
    pause(fast)

    # Step 2: Embedding Generation
    sample_desc = "Heavy Duty Nitrile Gloves Large Blue Powder Free 100ct"
    vec = model.encode([sample_desc], normalize_embeddings=True)[0].tolist()
    console.print(
        Panel(
            f"[bold cyan]Step 2: Converting Description to a 384-Dim Unit Vector[/bold cyan]\n"
            f"Input: [white]\"{sample_desc}\"[/white]\n"
            f"Model: [yellow]all-MiniLM-L6-v2[/yellow] (L2-normalized, ||v|| = 1.0)\n"
            f"First 8 dimensions: [green]{[round(x, 5) for x in vec[:8]]}[/green] ...",
            title="Dense Vector Embedding",
        )
    )
    pause(fast)

    # Step 3: MongoDB $vectorSearch Aggregation Pipeline
    pipeline_preview = [
        {
            "$vectorSearch": {
                "index": VENDOR_VECTOR_INDEX,
                "path": "description_embedding",
                "queryVector": "<384-dim float vector>",
                "numCandidates": 50,
                "limit": 3,
            }
        },
        {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
        {"$project": {"_id": 0, "description_embedding": 0}},
    ]
    console.print("[bold cyan]Step 3: MongoDB Atlas $vectorSearch Aggregation Pipeline[/bold cyan]")
    console.print(Syntax(json.dumps(pipeline_preview, indent=2), "json", theme="monokai"))

    matches = search_similar_items(sample_desc, target="vendor", top_k=3)
    render_matches(matches, f"Top 3 Vendor Matches for: \"{sample_desc}\"", target="vendor")
    pause(fast)

    # Step 4: Same-SKU vs Cross-SKU & Near-Miss Demo
    console.print("[bold cyan]Step 4: Batch Matching a Full Customer PO (PO-2026-105)[/bold cyan]")
    map_purchase_order("PO-2026-105", save=False)
    pause(fast)

    # Step 5: Summary of Saved Mappings
    mappings = list(db["sku_mappings"].find({}, {"_id": 0, "same_sku": 1, "similarity_score": 1}))
    same_cnt = sum(1 for m in mappings if m.get("same_sku"))
    cross_cnt = len(mappings) - same_cnt
    avg_score = sum(m.get("similarity_score", 0) for m in mappings) / len(mappings) if mappings else 0

    summary = Table(title="Step 5: Saved SKU Mappings Summary (purchase_order_poc.sku_mappings)")
    summary.add_column("Total Mappings", justify="right", style="cyan")
    summary.add_column("Same-SKU Mappings", justify="right", style="green")
    summary.add_column("Cross-SKU Mappings", justify="right", style="yellow")
    summary.add_column("Avg Cosine Score", justify="right", style="magenta")
    summary.add_row(str(len(mappings)), str(same_cnt), str(cross_cnt), f"{avg_score:.4f}")
    console.print(summary)
    console.print("\n[bold green]Demo complete![/bold green] Open [cyan]http://127.0.0.1:5000[/cyan] for the interactive Web UI.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a guided terminal demo of the POC.")
    parser.add_argument("--fast", action="store_true", help="Run without interactive pauses")
    args = parser.parse_args()
    run_demo(fast=args.fast)
