"""Similarity search (MongoDB Atlas $vectorSearch) and SKU mapping app."""

import argparse
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from config import (
    get_mongo_db,
    get_embedding_model,
    VENDOR_VECTOR_INDEX,
    CUSTOMER_VECTOR_INDEX,
)

console = Console()


def search_similar_items(
    description: str,
    target: str = "vendor",
    top_k: int = 5,
    vector_filter: dict | None = None,
) -> list[dict]:
    """Run a MongoDB Atlas $vectorSearch aggregation pipeline on item descriptions."""
    db = get_mongo_db()
    model = get_embedding_model()

    if target == "vendor":
        collection = db["vendor_catalog"]
        index_name = VENDOR_VECTOR_INDEX
    else:
        collection = db["customer_po_items"]
        index_name = CUSTOMER_VECTOR_INDEX

    query_vec = model.encode([description], normalize_embeddings=True)[0].tolist()

    vector_search_stage = {
        "index": index_name,
        "path": "description_embedding",
        "queryVector": query_vec,
        "numCandidates": max(top_k * 10, 50),
        "limit": top_k,
    }
    if vector_filter:
        vector_search_stage["filter"] = vector_filter

    pipeline = [
        {"$vectorSearch": vector_search_stage},
        {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
        {"$project": {"_id": 0, "description_embedding": 0}},
    ]

    docs = list(collection.aggregate(pipeline))
    matches = []
    for doc in docs:
        matches.append(
            {
                "sku": doc.get("sku", ""),
                "line_item_id": doc.get("line_item_id", ""),
                "description": doc.get("description", ""),
                "similarity": round(float(doc.get("score", 0.0)), 4),
                "metadata": doc,
            }
        )
    return matches


def save_sku_mapping(
    customer_sku: str,
    vendor_sku: str,
    customer_description: str,
    vendor_description: str,
    similarity_score: float,
    po_number: str | None = None,
    line_item_id: str | None = None,
    status: str = "MAPPED",
) -> dict:
    """Upsert a Customer SKU <-> Vendor SKU mapping into MongoDB."""
    db = get_mongo_db()
    now = datetime.now(timezone.utc)

    doc = {
        "customer_sku": customer_sku,
        "vendor_sku": vendor_sku,
        "same_sku": customer_sku == vendor_sku,
        "customer_description": customer_description,
        "vendor_description": vendor_description,
        "similarity_score": round(float(similarity_score), 4),
        "po_number": po_number,
        "line_item_id": line_item_id,
        "status": status,
        "updated_at": now,
    }

    db["sku_mappings"].update_one(
        {"customer_sku": customer_sku, "vendor_sku": vendor_sku},
        {"$set": doc, "$setOnInsert": {"created_at": now}},
        upsert=True,
    )
    return doc


def render_matches(matches: list[dict], title: str, target: str = "vendor") -> None:
    """Display $vectorSearch results in a formatted table."""
    table = Table(title=title, show_lines=True)
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Score", justify="right", style="green", no_wrap=True)
    table.add_column("SKU", style="bold yellow", no_wrap=True)
    table.add_column("Line Item ID", style="dim", no_wrap=True)
    table.add_column("Party / PO", style="magenta")
    table.add_column("Description", style="white")

    for idx, m in enumerate(matches, start=1):
        meta = m["metadata"]
        party = (
            meta.get("vendor_name", "")
            if target == "vendor"
            else f"{meta.get('po_number', '')} ({meta.get('customer_name', '')})"
        )
        table.add_row(
            str(idx),
            f"{m['similarity']:.4f}",
            m["sku"],
            m["line_item_id"],
            party,
            m["description"],
        )
    console.print(table)


def list_saved_mappings() -> None:
    """Fetch and display all saved SKU mappings from MongoDB."""
    db = get_mongo_db()
    mappings = list(db["sku_mappings"].find({}, {"_id": 0}).sort("updated_at", -1))

    if not mappings:
        console.print("[yellow]No SKU mappings saved yet.[/yellow]")
        return

    table = Table(title="Saved SKU Mappings (MongoDB: sku_mappings)", show_lines=True)
    table.add_column("Customer SKU", style="cyan", no_wrap=True)
    table.add_column("Vendor SKU", style="yellow", no_wrap=True)
    table.add_column("Same SKU?", justify="center", no_wrap=True)
    table.add_column("Score", justify="right", style="green", no_wrap=True)
    table.add_column("Customer Description")
    table.add_column("Vendor Description")

    for m in mappings:
        table.add_row(
            m["customer_sku"],
            m["vendor_sku"],
            "YES" if m.get("same_sku") else "NO",
            f"{m.get('similarity_score', 0):.4f}",
            m.get("customer_description", ""),
            m.get("vendor_description", ""),
        )
    console.print(table)


def map_purchase_order(po_number: str, save: bool = False, threshold: float = 0.65) -> None:
    """Find best vendor SKU matches for every line item in a Customer PO via $vectorSearch."""
    db = get_mongo_db()
    po = db["customer_purchase_orders"].find_one({"po_number": po_number}, {"_id": 0})
    if not po:
        console.print(f"[red]Purchase order '{po_number}' not found.[/red]")
        return

    console.print(
        f"\n[bold]PO:[/bold] {po['po_number']} | "
        f"[bold]Customer:[/bold] {po['customer_name']} ({po['customer_id']})"
    )

    table = Table(title=f"Line Item Mapping Suggestions for {po_number}", show_lines=True)
    table.add_column("Line ID", style="dim", no_wrap=True)
    table.add_column("Customer SKU", style="cyan", no_wrap=True)
    table.add_column("Matched Vendor SKU", style="yellow", no_wrap=True)
    table.add_column("Same SKU?", justify="center", no_wrap=True)
    table.add_column("Score", justify="right", style="green", no_wrap=True)
    table.add_column("Customer Desc")
    table.add_column("Matched Vendor Desc")

    saved_count = 0
    for li in po.get("line_items", []):
        matches = search_similar_items(li["description"], target="vendor", top_k=1)
        if not matches:
            continue
        best = matches[0]
        same_sku = li["sku"] == best["sku"]
        table.add_row(
            li["line_item_id"],
            li["sku"],
            best["sku"],
            "YES" if same_sku else "NO",
            f"{best['similarity']:.4f}",
            li["description"],
            best["description"],
        )
        if save and best["similarity"] >= threshold:
            save_sku_mapping(
                customer_sku=li["sku"],
                vendor_sku=best["sku"],
                customer_description=li["description"],
                vendor_description=best["description"],
                similarity_score=best["similarity"],
                po_number=po["po_number"],
                line_item_id=li["line_item_id"],
            )
            saved_count += 1

    console.print(table)
    if save:
        console.print(
            f"[green]Saved {saved_count} SKU mapping(s) (score >= {threshold}) to MongoDB.[/green]"
        )


def interactive_mode() -> None:
    """Run an interactive CLI session for MongoDB $vectorSearch and SKU mapping."""
    console.print("[bold cyan]Purchase Order SKU Similarity & Mapping POC (MongoDB Vector Search)[/bold cyan]")

    while True:
        console.print("\n[bold]Choose an action:[/bold]")
        console.print("  1. Search by description & create SKU mapping")
        console.print("  2. Auto-match a Customer PO against Vendor Catalog")
        console.print("  3. View saved SKU mappings")
        console.print("  4. Exit")

        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")

        if choice == "1":
            desc = Prompt.ask("Enter item description").strip()
            if not desc:
                continue
            target = Prompt.ask("Search against", choices=["vendor", "customer"], default="vendor")
            matches = search_similar_items(desc, target=target, top_k=5)
            render_matches(matches, f"Top Matches in {target.title()} Catalog ($vectorSearch)", target=target)

            if target == "vendor" and matches and Confirm.ask("Save a mapping to MongoDB?", default=True):
                pick = Prompt.ask(
                    "Pick match number",
                    choices=[str(i) for i in range(1, len(matches) + 1)],
                    default="1",
                )
                chosen = matches[int(pick) - 1]
                cust_sku = Prompt.ask("Enter Customer SKU (or leave same as vendor)", default=chosen["sku"])
                save_sku_mapping(
                    customer_sku=cust_sku,
                    vendor_sku=chosen["sku"],
                    customer_description=desc,
                    vendor_description=chosen["description"],
                    similarity_score=chosen["similarity"],
                )
                console.print(
                    f"[green]Saved mapping: {cust_sku} <-> {chosen['sku']} "
                    f"(score: {chosen['similarity']:.4f})[/green]"
                )

        elif choice == "2":
            db = get_mongo_db()
            pos = [p["po_number"] for p in db["customer_purchase_orders"].find({}, {"po_number": 1, "_id": 0})]
            if not pos:
                console.print("[red]No POs found in MongoDB. Run seed_db.py first.[/red]")
                continue
            po_num = Prompt.ask("Select PO number", choices=pos, default=pos[0])
            do_save = Confirm.ask("Save matched mappings to MongoDB?", default=True)
            map_purchase_order(po_num, save=do_save)

        elif choice == "3":
            list_saved_mappings()

        elif choice == "4":
            break


def main():
    parser = argparse.ArgumentParser(
        description="Run MongoDB Atlas $vectorSearch on item descriptions and map Customer <-> Vendor SKUs."
    )
    parser.add_argument("--desc", type=str, help="Item description to search for")
    parser.add_argument("--customer-sku", type=str, help="Customer SKU to pair with --desc")
    parser.add_argument(
        "--target",
        choices=["vendor", "customer", "both"],
        default="vendor",
        help="MongoDB collection to search (default: vendor)",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return (default: 5)")
    parser.add_argument(
        "--save-top",
        action="store_true",
        help="Automatically save the top vendor match as a SKU mapping in MongoDB",
    )
    parser.add_argument("--po", type=str, help="Match all line items of a Customer PO (e.g. PO-2026-101)")
    parser.add_argument("--save", action="store_true", help="Save PO line item mappings to MongoDB")
    parser.add_argument("--list-mappings", action="store_true", help="Display all saved SKU mappings")

    args = parser.parse_args()

    if args.list_mappings:
        list_saved_mappings()
        return

    if args.po:
        map_purchase_order(args.po, save=args.save)
        return

    if args.desc:
        targets = ["vendor", "customer"] if args.target == "both" else [args.target]
        for t in targets:
            matches = search_similar_items(args.desc, target=t, top_k=args.top_k)
            render_matches(
                matches,
                f"Top {args.top_k} {t.title()} Matches ($vectorSearch) for: \"{args.desc}\"",
                target=t,
            )

            if t == "vendor" and args.save_top and matches:
                if not args.customer_sku:
                    console.print("[red]--customer-sku is required when using --save-top.[/red]")
                    return
                best = matches[0]
                save_sku_mapping(
                    customer_sku=args.customer_sku,
                    vendor_sku=best["sku"],
                    customer_description=args.desc,
                    vendor_description=best["description"],
                    similarity_score=best["similarity"],
                )
                console.print(
                    f"[green]Saved mapping: {args.customer_sku} <-> {best['sku']} "
                    f"(score: {best['similarity']:.4f})[/green]"
                )
        return

    interactive_mode()


if __name__ == "__main__":
    main()
