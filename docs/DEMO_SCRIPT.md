# Live Demo Presenter Script (5–7 Minutes)

## Before You Start
1. Ensure the Flask Web UI is running:
   ```bash
   python web_app.py
   ```
2. Open **http://127.0.0.1:5000** in your browser.
3. *(Optional)* Have a terminal ready for the automated CLI demo:
   ```bash
   python demo.py
   ```

---

## Part 1 — Set the Problem (1 min)
- **Talking point**: *"In B2B procurement, customers send Purchase Orders with their own SKUs and descriptions, while vendors maintain their own catalogs. Sometimes both sides share the same SKU with slightly different wording; other times the SKUs are completely different and descriptions use abbreviations or different units."*
- **On Screen**: Point to the **KPI strip** at the top of `http://127.0.0.1:5000` (`40` Vendor Catalog items, `6` Customer POs / `24` Line Items).
- Click **Tab 4: Data Explorer (Both Ends)** and filter by `Nitrile` or `Bolt` to show the vendor catalog items stored in MongoDB Atlas.

---

## Part 2 — Live `$vectorSearch` on a Description (2 mins)
- **On Screen**: Switch to **Tab 1: Description Search & Map**.
- Click the sample chip **`Nitrile Gloves Large (Cross SKU)`**:
  - Input: `"Heavy Duty Nitrile Gloves Large Blue Powder Free 100ct"`
  - Customer SKU: `CUST-GLV-LRG`
- **Talking point**: *"We convert this text into a 384-dimensional unit vector using `all-MiniLM-L6-v2` and run a MongoDB Atlas `$vectorSearch` aggregation pipeline against `vendor_vector_index`."*
- Click **Inspect `$vectorSearch` Pipeline & Vector** to show the exact `$vectorSearch` JSON stage and the first 8 dimensions of the query vector.
- Point out that `VND-GLV-L100` (`Size L`) ranks #1 above `VND-GLV-M100` (`Size M`), even though the words *"Heavy Duty"* and *"100ct"* differ from *"Disposable Exam"* and *"Box of 100"*.
- Click **Map SKU** on row #1 to upsert `CUST-GLV-LRG ↔ VND-GLV-L100` into `sku_mappings`.

---

## Part 3 — Near-Miss Edge Case (1 min)
- Click the sample chip **`Isopropyl Alcohol 1L (Unit Conversion)`**.
- **Talking point**: *"Notice how `500mL` and `1000mL` score almost identically in pure semantic space (`~0.72`). Returning Top-K results lets the user pick `VND-IPA-1000` (`1000mL` = `1 Liter`) instead of blindly trusting #1."*

---

## Part 4 — Batch Matching a Customer PO (1.5 mins)
- Switch to **Tab 2: Customer PO Matcher**.
- Select **`PO-2026-105 — VoltGrid Facilities Inc (5 items)`**.
- Click **Find Top Vendor Matches**:
  - Point out **Cross-SKU** matches (`VG-THHN-12B ↔ VND-WIRE-12AWG-BLK`) alongside **Same-SKU** matches (`SKU-BRKR-20A-1P ↔ SKU-BRKR-20A-1P`, `SKU-VEST-HIVIS-XL ↔ SKU-VEST-HIVIS-XL`).
- Click **Auto-Match & Save All** to persist all 5 mappings to MongoDB.

---

## Part 5 — Review Persisted Mappings (1 min)
- Switch to **Tab 3: Saved SKU Mappings**.
- Use the dropdown to toggle between **All Mappings**, **Same SKU Only**, and **Cross-SKU Only**.
- **Closing point**: *"All operational data, 384-dim embeddings, HNSW vector indexes, `$vectorSearch` queries, and confirmed SKU mappings live in a single MongoDB Atlas database (`purchase_order_poc`)."*
