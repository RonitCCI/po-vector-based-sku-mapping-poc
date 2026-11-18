"""Seed MongoDB with synthetic Customer Purchase Orders and Vendor Catalog data."""

from datetime import datetime, timezone
from pymongo import ASCENDING
from config import get_mongo_db

VENDOR_ITEMS = [
    # --- Industrial Hardware & Fasteners ---
    {
        "line_item_id": "VLI-001",
        "sku": "SKU-BOLT-M8-40",
        "vendor_id": "VND-APEX",
        "vendor_name": "Apex Industrial Supply",
        "category": "Fasteners",
        "description": "SS304 Hex Head Bolt M8x40mm, Corrosion Resistant (Box of 50)",
        "uom": "BOX",
        "unit_price": 18.50,
    },
    {
        "line_item_id": "VLI-002",
        "sku": "VND-BLT-M6-40",
        "vendor_id": "VND-APEX",
        "vendor_name": "Apex Industrial Supply",
        "category": "Fasteners",
        "description": "SS304 Hex Head Bolt M6x40mm, Corrosion Resistant (Box of 50)",
        "uom": "BOX",
        "unit_price": 14.00,
    },
    {
        "line_item_id": "VLI-003",
        "sku": "VND-NUT-M8-SS",
        "vendor_id": "VND-APEX",
        "vendor_name": "Apex Industrial Supply",
        "category": "Fasteners",
        "description": "M8 Metric Hex Flange Nut, 304 Stainless Steel, 100 Pack",
        "uom": "PK",
        "unit_price": 11.25,
    },
    {
        "line_item_id": "VLI-004",
        "sku": "SKU-WSHR-M8",
        "vendor_id": "VND-APEX",
        "vendor_name": "Apex Industrial Supply",
        "category": "Fasteners",
        "description": "Flat Washer M8 Stainless Steel DIN 125 (100/Pkg)",
        "uom": "PK",
        "unit_price": 6.75,
    },
    # --- Safety & PPE ---
    {
        "line_item_id": "VLI-005",
        "sku": "VND-GLV-L100",
        "vendor_id": "VND-SAFEPRO",
        "vendor_name": "SafePro PPE Distributors",
        "category": "Safety",
        "description": "Disposable Nitrile Exam Gloves, Size L, Blue, Powder-Free, Box of 100",
        "uom": "BOX",
        "unit_price": 12.90,
    },
    {
        "line_item_id": "VLI-006",
        "sku": "VND-GLV-M100",
        "vendor_id": "VND-SAFEPRO",
        "vendor_name": "SafePro PPE Distributors",
        "category": "Safety",
        "description": "Disposable Nitrile Exam Gloves, Size M, Blue, Powder-Free, Box of 100",
        "uom": "BOX",
        "unit_price": 12.90,
    },
    {
        "line_item_id": "VLI-007",
        "sku": "SKU-GOGGLE-CLR",
        "vendor_id": "VND-SAFEPRO",
        "vendor_name": "SafePro PPE Distributors",
        "category": "Safety",
        "description": "Anti-Fog Clear Safety Goggles, ANSI Z87.1 Impact Rated",
        "uom": "EA",
        "unit_price": 8.40,
    },
    # --- Chemicals & Maintenance ---
    {
        "line_item_id": "VLI-008",
        "sku": "VND-IPA-1000",
        "vendor_id": "VND-CHEMCORE",
        "vendor_name": "ChemCore Solutions",
        "category": "Chemicals",
        "description": "IPA 99.9% Technical Grade Isopropyl Alcohol Solvent 1000mL",
        "uom": "BTL",
        "unit_price": 15.60,
    },
    {
        "line_item_id": "VLI-009",
        "sku": "VND-IPA-500",
        "vendor_id": "VND-CHEMCORE",
        "vendor_name": "ChemCore Solutions",
        "category": "Chemicals",
        "description": "IPA 99.9% Technical Grade Isopropyl Alcohol Solvent 500mL",
        "uom": "BTL",
        "unit_price": 9.20,
    },
    {
        "line_item_id": "VLI-010",
        "sku": "VND-LUB-WD400",
        "vendor_id": "VND-CHEMCORE",
        "vendor_name": "ChemCore Solutions",
        "category": "Chemicals",
        "description": "Multi-Purpose Penetrating Lubricant Spray 400mL Aerosol Can",
        "uom": "CAN",
        "unit_price": 7.80,
    },
    # --- Electrical & IT ---
    {
        "line_item_id": "VLI-011",
        "sku": "SKU-CAT6-10FT",
        "vendor_id": "VND-TECHLINK",
        "vendor_name": "TechLink Components",
        "category": "Networking",
        "description": "Cat6 Gigabit Ethernet Patch Cable 10ft Snagless RJ45 Blue",
        "uom": "EA",
        "unit_price": 5.50,
    },
    {
        "line_item_id": "VLI-012",
        "sku": "VND-ETH-C6-25",
        "vendor_id": "VND-TECHLINK",
        "vendor_name": "TechLink Components",
        "category": "Networking",
        "description": "Cat6 Gigabit Ethernet Patch Cable 25ft Snagless RJ45 Blue",
        "uom": "EA",
        "unit_price": 9.95,
    },
    {
        "line_item_id": "VLI-013",
        "sku": "VND-SSD-1TB-NV",
        "vendor_id": "VND-TECHLINK",
        "vendor_name": "TechLink Components",
        "category": "Storage",
        "description": "1TB M.2 NVMe PCIe Gen4 Internal Solid State Drive",
        "uom": "EA",
        "unit_price": 79.00,
    },
    {
        "line_item_id": "VLI-014",
        "sku": "VND-PWR-65W-USBC",
        "vendor_id": "VND-TECHLINK",
        "vendor_name": "TechLink Components",
        "category": "Power",
        "description": "65W USB-C PD Laptop Power Adapter Charger with 6ft Cord",
        "uom": "EA",
        "unit_price": 24.50,
    },
    # --- Packaging & Warehouse ---
    {
        "line_item_id": "VLI-015",
        "sku": "VND-TAPE-CLR-6",
        "vendor_id": "VND-PACKPRO",
        "vendor_name": "PackPro Logistics",
        "category": "Packaging",
        "description": "Heavy Duty Clear Acrylic Carton Sealing Tape 2in x 110yd (6 Rolls)",
        "uom": "PK",
        "unit_price": 19.80,
    },
    {
        "line_item_id": "VLI-016",
        "sku": "SKU-BOX-12X12",
        "vendor_id": "VND-PACKPRO",
        "vendor_name": "PackPro Logistics",
        "category": "Packaging",
        "description": "Corrugated Cardboard Shipping Boxes 12x12x12 Inch ECT-32 (Bundle of 25)",
        "uom": "BDL",
        "unit_price": 32.00,
    },
    {
        "line_item_id": "VLI-017",
        "sku": "VND-STRETCH-18",
        "vendor_id": "VND-PACKPRO",
        "vendor_name": "PackPro Logistics",
        "category": "Packaging",
        "description": "Hand Stretch Pallet Wrap Film 18in x 1500ft 80 Gauge Clear (4 Rolls)",
        "uom": "CS",
        "unit_price": 48.00,
    },
    # --- Electrical & Wiring ---
    {
        "line_item_id": "VLI-018",
        "sku": "VND-WIRE-12AWG-BLK",
        "vendor_id": "VND-VOLTMAX",
        "vendor_name": "VoltMax Electrical",
        "category": "Electrical",
        "description": "12 AWG THHN Stranded Copper Building Wire Black 500ft Spool",
        "uom": "SPL",
        "unit_price": 89.50,
    },
    {
        "line_item_id": "VLI-019",
        "sku": "VND-WIRE-14AWG-BLK",
        "vendor_id": "VND-VOLTMAX",
        "vendor_name": "VoltMax Electrical",
        "category": "Electrical",
        "description": "14 AWG THHN Stranded Copper Building Wire Black 500ft Spool",
        "uom": "SPL",
        "unit_price": 64.00,
    },
    {
        "line_item_id": "VLI-020",
        "sku": "SKU-BRKR-20A-1P",
        "vendor_id": "VND-VOLTMAX",
        "vendor_name": "VoltMax Electrical",
        "category": "Electrical",
        "description": "20 Amp Single-Pole 120/240V Thermal Magnetic Circuit Breaker",
        "uom": "EA",
        "unit_price": 14.75,
    },
    {
        "line_item_id": "VLI-021",
        "sku": "VND-TIE-11IN-UV",
        "vendor_id": "VND-VOLTMAX",
        "vendor_name": "VoltMax Electrical",
        "category": "Electrical",
        "description": "UV Resistant Black Nylon Cable Zip Ties 11 Inch 50lb Tensile (100 Pack)",
        "uom": "PK",
        "unit_price": 9.40,
    },
    {
        "line_item_id": "VLI-022",
        "sku": "VND-LED-T8-4FT",
        "vendor_id": "VND-VOLTMAX",
        "vendor_name": "VoltMax Electrical",
        "category": "Lighting",
        "description": "4ft T8 LED Tube Light 18W 5000K Daylight Ballast Bypass (Case of 10)",
        "uom": "CS",
        "unit_price": 68.00,
    },
    # --- Bearings & Mechanical ---
    {
        "line_item_id": "VLI-023",
        "sku": "SKU-BRG-6204-2RS",
        "vendor_id": "VND-MECHPRO",
        "vendor_name": "MechPro Bearings & Motion",
        "category": "Bearings",
        "description": "6204-2RS Deep Groove Ball Bearing 20x47x14mm Double Rubber Sealed",
        "uom": "EA",
        "unit_price": 6.20,
    },
    {
        "line_item_id": "VLI-024",
        "sku": "VND-BRG-6205-2RS",
        "vendor_id": "VND-MECHPRO",
        "vendor_name": "MechPro Bearings & Motion",
        "category": "Bearings",
        "description": "6205-2RS Deep Groove Ball Bearing 25x52x15mm Double Rubber Sealed",
        "uom": "EA",
        "unit_price": 7.90,
    },
    {
        "line_item_id": "VLI-025",
        "sku": "VND-BELT-A42",
        "vendor_id": "VND-MECHPRO",
        "vendor_name": "MechPro Bearings & Motion",
        "category": "Power Transmission",
        "description": "Classical V-Belt A42 1/2 Inch Top Width x 44 Inch Outside Length",
        "uom": "EA",
        "unit_price": 11.50,
    },
    # --- Pneumatics & Valves ---
    {
        "line_item_id": "VLI-026",
        "sku": "VND-PNEU-ELB-14",
        "vendor_id": "VND-FLUIDTECH",
        "vendor_name": "FluidTech Pneumatics",
        "category": "Pneumatics",
        "description": "1/4 Inch OD Tube x 1/4 NPT Male Swivel Elbow Push-to-Connect Fitting (10 Pack)",
        "uom": "PK",
        "unit_price": 16.40,
    },
    {
        "line_item_id": "VLI-027",
        "sku": "VND-PNEU-ELB-38",
        "vendor_id": "VND-FLUIDTECH",
        "vendor_name": "FluidTech Pneumatics",
        "category": "Pneumatics",
        "description": "3/8 Inch OD Tube x 3/8 NPT Male Swivel Elbow Push-to-Connect Fitting (10 Pack)",
        "uom": "PK",
        "unit_price": 21.00,
    },
    {
        "line_item_id": "VLI-028",
        "sku": "SKU-VLV-BALL-1IN",
        "vendor_id": "VND-FLUIDTECH",
        "vendor_name": "FluidTech Pneumatics",
        "category": "Valves",
        "description": "1 Inch Brass Full Port Ball Valve Female NPT Threaded 600 WOG",
        "uom": "EA",
        "unit_price": 19.25,
    },
    {
        "line_item_id": "VLI-029",
        "sku": "VND-HOSE-AIR-50",
        "vendor_id": "VND-FLUIDTECH",
        "vendor_name": "FluidTech Pneumatics",
        "category": "Pneumatics",
        "description": "3/8 Inch x 50ft Hybrid Polymer Air Compressor Hose 300 PSI with 1/4 NPT Fittings",
        "uom": "EA",
        "unit_price": 38.50,
    },
    # --- IT & Office Equipment ---
    {
        "line_item_id": "VLI-030",
        "sku": "VND-MON-27-IPS",
        "vendor_id": "VND-TECHLINK",
        "vendor_name": "TechLink Components",
        "category": "Displays",
        "description": "27 Inch QHD 2560x1440 IPS Business Monitor HDMI DisplayPort USB-C",
        "uom": "EA",
        "unit_price": 249.00,
    },
    {
        "line_item_id": "VLI-031",
        "sku": "VND-MON-24-FHD",
        "vendor_id": "VND-TECHLINK",
        "vendor_name": "TechLink Components",
        "category": "Displays",
        "description": "24 Inch Full HD 1920x1080 IPS Office Monitor HDMI DisplayPort",
        "uom": "EA",
        "unit_price": 159.00,
    },
    {
        "line_item_id": "VLI-032",
        "sku": "SKU-DOCK-USBC-DUAL",
        "vendor_id": "VND-TECHLINK",
        "vendor_name": "TechLink Components",
        "category": "Accessories",
        "description": "USB-C Dual 4K HDMI Docking Station with 100W Power Delivery and Gigabit Ethernet",
        "uom": "EA",
        "unit_price": 129.00,
    },
    {
        "line_item_id": "VLI-033",
        "sku": "VND-PAPER-A4-5R",
        "vendor_id": "VND-OFFICEHUB",
        "vendor_name": "OfficeHub Supplies",
        "category": "Paper",
        "description": "A4 Copy & Printer Paper 80gsm Bright White 500 Sheets/Ream (Case of 5 Reams)",
        "uom": "CS",
        "unit_price": 28.50,
    },
    {
        "line_item_id": "VLI-034",
        "sku": "VND-PAPER-LTR-10R",
        "vendor_id": "VND-OFFICEHUB",
        "vendor_name": "OfficeHub Supplies",
        "category": "Paper",
        "description": "US Letter 8.5x11 Copy Paper 20lb 92 Bright (Case of 10 Reams / 5000 Sheets)",
        "uom": "CS",
        "unit_price": 46.00,
    },
    {
        "line_item_id": "VLI-035",
        "sku": "VND-TONER-HP58A",
        "vendor_id": "VND-OFFICEHUB",
        "vendor_name": "OfficeHub Supplies",
        "category": "Printing",
        "description": "CF258A 58A Black High-Yield LaserJet Toner Cartridge 3000 Pages",
        "uom": "EA",
        "unit_price": 94.00,
    },
    # --- Tools & Janitorial ---
    {
        "line_item_id": "VLI-036",
        "sku": "VND-DRILL-18V-KIT",
        "vendor_id": "VND-MECHPRO",
        "vendor_name": "MechPro Bearings & Motion",
        "category": "Tools",
        "description": "18V Brushless Cordless Hammer Drill Driver Kit with 2x 5.0Ah Batteries & Charger",
        "uom": "KIT",
        "unit_price": 189.00,
    },
    {
        "line_item_id": "VLI-037",
        "sku": "SKU-TORQ-38-DR",
        "vendor_id": "VND-MECHPRO",
        "vendor_name": "MechPro Bearings & Motion",
        "category": "Tools",
        "description": "3/8 Inch Drive Micrometer Click Torque Wrench 10-80 ft-lbs",
        "uom": "EA",
        "unit_price": 54.00,
    },
    {
        "line_item_id": "VLI-038",
        "sku": "VND-WIPES-IND-80",
        "vendor_id": "VND-SAFEPRO",
        "vendor_name": "SafePro PPE Distributors",
        "category": "Janitorial",
        "description": "Heavy Duty Industrial Hand & Tool Cleaning Wipes Bucket (80 Count)",
        "uom": "BKT",
        "unit_price": 14.20,
    },
    {
        "line_item_id": "VLI-039",
        "sku": "VND-EARPLUG-200",
        "vendor_id": "VND-SAFEPRO",
        "vendor_name": "SafePro PPE Distributors",
        "category": "Safety",
        "description": "Uncorded Foam Earplugs NRR 32dB Hearing Protection (Box of 200 Pairs)",
        "uom": "BOX",
        "unit_price": 22.75,
    },
    {
        "line_item_id": "VLI-040",
        "sku": "SKU-VEST-HIVIS-XL",
        "vendor_id": "VND-SAFEPRO",
        "vendor_name": "SafePro PPE Distributors",
        "category": "Safety",
        "description": "ANSI Class 2 High Visibility Reflective Safety Vest Lime Yellow Size XL",
        "uom": "EA",
        "unit_price": 11.80,
    },
]

CUSTOMER_PURCHASE_ORDERS = [
    {
        "po_number": "PO-2026-101",
        "customer_id": "CUST-ACME",
        "customer_name": "Acme Manufacturing Corp",
        "order_date": "2026-11-10",
        "status": "OPEN",
        "line_items": [
            {
                "line_item_id": "CLI-101-1",
                # Same SKU as vendor, slightly different wording
                "sku": "SKU-BOLT-M8-40",
                "description": "Stainless Steel Hex Bolt M8 x 40mm - Pack of 50",
                "quantity": 10,
                "uom": "BOX",
                "unit_price": 18.50,
            },
            {
                "line_item_id": "CLI-101-2",
                # Different SKU, paraphrased description
                "sku": "CUST-GLV-LRG",
                "description": "Heavy Duty Nitrile Gloves Large Blue Powder Free 100ct",
                "quantity": 25,
                "uom": "BOX",
                "unit_price": 13.00,
            },
            {
                "line_item_id": "CLI-101-3",
                # Different SKU, unit conversion (1 Liter vs 1000mL)
                "sku": "CUST-CHEM-IPA1L",
                "description": "Isopropyl Alcohol 99% Pure Cleaning Solvent 1 Liter Bottle",
                "quantity": 12,
                "uom": "BTL",
                "unit_price": 15.60,
            },
            {
                "line_item_id": "CLI-101-4",
                # Same SKU as vendor, near-identical description
                "sku": "SKU-WSHR-M8",
                "description": "Flat Washer M8 Stainless Steel DIN 125 (100 Pack)",
                "quantity": 15,
                "uom": "PK",
                "unit_price": 6.75,
            },
        ],
    },
    {
        "po_number": "PO-2026-102",
        "customer_id": "CUST-NOVA",
        "customer_name": "Nova Systems Ltd",
        "order_date": "2026-11-12",
        "status": "OPEN",
        "line_items": [
            {
                "line_item_id": "CLI-102-1",
                # Same SKU as vendor
                "sku": "SKU-CAT6-10FT",
                "description": "10 ft Cat6 Network Patch Cord RJ45 Blue Snagless",
                "quantity": 40,
                "uom": "EA",
                "unit_price": 5.50,
            },
            {
                "line_item_id": "CLI-102-2",
                # Different SKU
                "sku": "NV-SSD-1000G",
                "description": "NVMe M.2 PCIe 4.0 Internal SSD 1TB",
                "quantity": 8,
                "uom": "EA",
                "unit_price": 79.00,
            },
            {
                "line_item_id": "CLI-102-3",
                # Different SKU
                "sku": "NV-CHG-65W",
                "description": "USB Type-C 65W Power Delivery Laptop Charger Adapter",
                "quantity": 15,
                "uom": "EA",
                "unit_price": 24.50,
            },
        ],
    },
    {
        "po_number": "PO-2026-103",
        "customer_id": "CUST-ACME",
        "customer_name": "Acme Manufacturing Corp",
        "order_date": "2026-11-15",
        "status": "OPEN",
        "line_items": [
            {
                "line_item_id": "CLI-103-1",
                # Different SKU
                "sku": "CUST-PKG-TAPE6",
                "description": "Clear Packing Tape 2 inch x 110 yards Heavy Duty 6-Pack",
                "quantity": 20,
                "uom": "PK",
                "unit_price": 19.80,
            },
            {
                "line_item_id": "CLI-103-2",
                # Same SKU as vendor
                "sku": "SKU-BOX-12X12",
                "description": "12x12x12 Corrugated Cardboard Shipping Cartons (25/Bundle)",
                "quantity": 10,
                "uom": "BDL",
                "unit_price": 32.00,
            },
            {
                "line_item_id": "CLI-103-3",
                # Same SKU as vendor
                "sku": "SKU-GOGGLE-CLR",
                "description": "Clear Protective Safety Goggles Anti-Fog ANSI Z87.1",
                "quantity": 30,
                "uom": "EA",
                "unit_price": 8.40,
            },
        ],
    },
    {
        "po_number": "PO-2026-104",
        "customer_id": "CUST-APEXM",
        "customer_name": "Apex Motors & Assembly",
        "order_date": "2026-11-16",
        "status": "OPEN",
        "line_items": [
            {
                "line_item_id": "CLI-104-1",
                "sku": "SKU-BRG-6204-2RS",
                "description": "Ball Bearing 6204-2RS Sealed 20mm Bore x 47mm OD x 14mm Width",
                "quantity": 24,
                "uom": "EA",
                "unit_price": 6.20,
            },
            {
                "line_item_id": "CLI-104-2",
                "sku": "AM-PNEU-14ELB",
                "description": "Pneumatic Push-to-Connect Male Elbow 1/4 Tube x 1/4 NPT (Pack of 10)",
                "quantity": 6,
                "uom": "PK",
                "unit_price": 16.40,
            },
            {
                "line_item_id": "CLI-104-3",
                "sku": "SKU-VLV-BALL-1IN",
                "description": "1\" NPT Female Brass Ball Valve Full Port 600 PSI WOG",
                "quantity": 8,
                "uom": "EA",
                "unit_price": 19.25,
            },
            {
                "line_item_id": "CLI-104-4",
                "sku": "AM-AIRHOSE-50",
                "description": "50 Foot Hybrid Air Hose 3/8in ID 300 PSI with 1/4in NPT Ends",
                "quantity": 4,
                "uom": "EA",
                "unit_price": 38.50,
            },
            {
                "line_item_id": "CLI-104-5",
                "sku": "SKU-TORQ-38-DR",
                "description": "Click-Type Torque Wrench 3/8in Drive 10 to 80 ft-lb",
                "quantity": 3,
                "uom": "EA",
                "unit_price": 54.00,
            },
        ],
    },
    {
        "po_number": "PO-2026-105",
        "customer_id": "CUST-VOLTGRID",
        "customer_name": "VoltGrid Facilities Inc",
        "order_date": "2026-11-17",
        "status": "OPEN",
        "line_items": [
            {
                "line_item_id": "CLI-105-1",
                "sku": "VG-THHN-12B",
                "description": "Black Copper Building Wire 12 AWG THHN Stranded 500 Foot Reel",
                "quantity": 4,
                "uom": "SPL",
                "unit_price": 89.50,
            },
            {
                "line_item_id": "CLI-105-2",
                "sku": "SKU-BRKR-20A-1P",
                "description": "Single Pole 20A Circuit Breaker 120/240V Thermal Magnetic",
                "quantity": 12,
                "uom": "EA",
                "unit_price": 14.75,
            },
            {
                "line_item_id": "CLI-105-3",
                "sku": "VG-ZIPTIE-11B",
                "description": "Black UV Nylon Zip Ties 11in 50lb Strength 100ct Bag",
                "quantity": 10,
                "uom": "PK",
                "unit_price": 9.40,
            },
            {
                "line_item_id": "CLI-105-4",
                "sku": "VG-LEDT8-4FT",
                "description": "4 Foot LED T8 Replacement Tube 18W 5000K Direct Wire (10-Pack)",
                "quantity": 5,
                "uom": "CS",
                "unit_price": 68.00,
            },
            {
                "line_item_id": "CLI-105-5",
                "sku": "SKU-VEST-HIVIS-XL",
                "description": "High-Vis Lime Yellow Reflective Safety Vest Class 2 X-Large",
                "quantity": 20,
                "uom": "EA",
                "unit_price": 11.80,
            },
        ],
    },
    {
        "po_number": "PO-2026-106",
        "customer_id": "CUST-NOVA",
        "customer_name": "Nova Systems Ltd",
        "order_date": "2026-11-18",
        "status": "OPEN",
        "line_items": [
            {
                "line_item_id": "CLI-106-1",
                "sku": "NV-MON-27Q",
                "description": "27-Inch IPS 1440p QHD Monitor with USB-C HDMI and DisplayPort",
                "quantity": 6,
                "uom": "EA",
                "unit_price": 249.00,
            },
            {
                "line_item_id": "CLI-106-2",
                "sku": "SKU-DOCK-USBC-DUAL",
                "description": "Dual 4K HDMI USB-C Laptop Dock 100W PD Charging Gigabit LAN",
                "quantity": 6,
                "uom": "EA",
                "unit_price": 129.00,
            },
            {
                "line_item_id": "CLI-106-3",
                "sku": "NV-TONER-58A",
                "description": "HP 58A CF258A Black Laser Toner Cartridge 3000 Page Yield",
                "quantity": 4,
                "uom": "EA",
                "unit_price": 94.00,
            },
            {
                "line_item_id": "CLI-106-4",
                "sku": "NV-WRAP-18IN",
                "description": "18 Inch x 1500ft Clear Pallet Stretch Wrap 80ga (4 Rolls/Case)",
                "quantity": 8,
                "uom": "CS",
                "unit_price": 48.00,
            },
        ],
    },
]


def seed_database():
    """Reset and seed vendor_catalog, customer_purchase_orders, and sku_mappings."""
    db = get_mongo_db()
    now = datetime.now(timezone.utc)

    # 1. Seed Vendor Catalog
    vendor_col = db["vendor_catalog"]
    vendor_col.delete_many({})
    vendor_docs = [{**item, "updated_at": now} for item in VENDOR_ITEMS]
    vendor_col.insert_many(vendor_docs)
    vendor_col.create_index([("sku", ASCENDING)], unique=True)

    # 2. Seed Customer Purchase Orders + flattened Customer PO Line Items
    po_col = db["customer_purchase_orders"]
    po_col.delete_many({})
    po_docs = [{**po, "updated_at": now} for po in CUSTOMER_PURCHASE_ORDERS]
    po_col.insert_many(po_docs)
    po_col.create_index([("po_number", ASCENDING)], unique=True)

    cli_col = db["customer_po_items"]
    cli_col.delete_many({})
    cli_docs = []
    for po in CUSTOMER_PURCHASE_ORDERS:
        for li in po["line_items"]:
            cli_docs.append(
                {
                    **li,
                    "po_number": po["po_number"],
                    "customer_id": po["customer_id"],
                    "customer_name": po["customer_name"],
                    "order_date": po["order_date"],
                    "updated_at": now,
                }
            )
    if cli_docs:
        cli_col.insert_many(cli_docs)
        cli_col.create_index([("line_item_id", ASCENDING)], unique=True)

    # 3. Ensure sku_mappings collection & unique index exist
    mappings_col = db["sku_mappings"]
    mappings_col.create_index(
        [("customer_sku", ASCENDING), ("vendor_sku", ASCENDING)],
        unique=True,
    )

    print(f"Seeded {len(vendor_docs)} vendor catalog items into '{db.name}.vendor_catalog'.")
    print(
        f"Seeded {len(po_docs)} customer purchase orders into '{db.name}.customer_purchase_orders' "
        f"and {len(cli_docs)} line items into '{db.name}.customer_po_items'."
    )
    print(f"Verified '{db.name}.sku_mappings' collection and indexes.")


if __name__ == "__main__":
    seed_database()
