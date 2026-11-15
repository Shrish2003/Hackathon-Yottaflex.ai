"""
Enterprise B2B product catalog and customer account master data templates.
"""

from decimal import Decimal
from typing import List, Dict, Any

# 25 Realistic B2B Enterprise Technology Products & Services
PRODUCT_CATALOG: List[Dict[str, Any]] = [
    {"sku": "SRV-COMP-8U", "name": "Enterprise 8U Rack Compute Node", "unit_price": Decimal("245000.00"), "category": "Hardware"},
    {"sku": "SRV-EDGE-1U", "name": "Edge AI Inference Microserver 1U", "unit_price": Decimal("85000.00"), "category": "Hardware"},
    {"sku": "SAN-STOR-100T", "name": "NVMe-oF High IOPS Storage Array 100TB", "unit_price": Decimal("520000.00"), "category": "Hardware"},
    {"sku": "NET-SW-100G", "name": "48-Port 100GbE Spine-Leaf Switch", "unit_price": Decimal("185000.00"), "category": "Hardware"},
    {"sku": "NET-ROUT-WAN", "name": "Redundant SD-WAN Gateway Router", "unit_price": Decimal("95000.00"), "category": "Hardware"},
    {"sku": "SEC-NGFW-500", "name": "Next-Gen Enterprise Firewall Appliance", "unit_price": Decimal("140000.00"), "category": "Security"},
    {"sku": "SEC-EDR-SEAT", "name": "Endpoint Detection & Response (Annual Seat)", "unit_price": Decimal("3500.00"), "category": "Software"},
    {"sku": "SEC-SIEM-LOG", "name": "Centralized SIEM Log Ingestion (1TB/mo)", "unit_price": Decimal("48000.00"), "category": "Software"},
    {"sku": "CLD-K8S-CLUST", "name": "Dedicated Managed Kubernetes Cluster (Mo)", "unit_price": Decimal("65000.00"), "category": "Cloud"},
    {"sku": "CLD-DB-PGSQL", "name": "High-Availability PostgreSQL DB Node (Mo)", "unit_price": Decimal("42000.00"), "category": "Cloud"},
    {"sku": "CLD-BANDWIDTH", "name": "Direct Cloud Interconnect Bandwidth 1Gbps", "unit_price": Decimal("28000.00"), "category": "Cloud"},
    {"sku": "ERP-CORP-LIC", "name": "Enterprise ERP Core License (Annual)", "unit_price": Decimal("750000.00"), "category": "Software"},
    {"sku": "ERP-USER-SEAT", "name": "ERP Financial User Named Seat (Annual)", "unit_price": Decimal("12500.00"), "category": "Software"},
    {"sku": "CRM-CORP-SEAT", "name": "CRM Enterprise Sales Seat (Annual)", "unit_price": Decimal("9800.00"), "category": "Software"},
    {"sku": "BI-ANALYTICS", "name": "Executive Revenue Analytics Suite (Annual)", "unit_price": Decimal("180000.00"), "category": "Software"},
    {"sku": "AI-INF-TOKEN", "name": "Enterprise LLM Inference API Token Pack (100M)", "unit_price": Decimal("35000.00"), "category": "Cloud"},
    {"sku": "SRV-MEM-128G", "name": "ECC DDR5 High-Speed Server RAM 128GB", "unit_price": Decimal("22000.00"), "category": "Hardware"},
    {"sku": "SRV-SSD-30TB", "name": "Enterprise PCIe Gen5 U.2 NVMe SSD 30.72TB", "unit_price": Decimal("165000.00"), "category": "Hardware"},
    {"sku": "NET-OPT-TRANS", "name": "100G QSFP28 Optical Transceiver Pair", "unit_price": Decimal("14500.00"), "category": "Hardware"},
    {"sku": "UPS-MOD-20KW", "name": "Modular Modular Data Center UPS 20kVA", "unit_price": Decimal("310000.00"), "category": "Infrastructure"},
    {"sku": "CONS-ENG-DAY", "name": "Principal Solutions Architect Consulting (Day)", "unit_price": Decimal("45000.00"), "category": "Services"},
    {"sku": "CONS-MIG-PACK", "name": "Cloud Database Migration Implementation Pack", "unit_price": Decimal("250000.00"), "category": "Services"},
    {"sku": "SUPP-247-PREM", "name": "24x7 Mission-Critical SLA Support (Annual)", "unit_price": Decimal("320000.00"), "category": "Services"},
    {"sku": "TRN-CORP-WK", "name": "Corporate DevOps & Security Training Bootcamp", "unit_price": Decimal("120000.00"), "category": "Services"},
    {"sku": "SEC-PEN-TEST", "name": "External Perimeter Vulnerability Assessment", "unit_price": Decimal("195000.00"), "category": "Services"},
]

# 100 Major Enterprise Accounts
ENTERPRISE_CUSTOMERS: List[Dict[str, Any]] = [
    {"name": "Tata Consultancy Services Ltd", "terms": "NET30", "limit": Decimal("15000000.00")},
    {"name": "Infosys Technologies Ltd", "terms": "NET30", "limit": Decimal("12000000.00")},
    {"name": "Wipro Enterprises Global", "terms": "NET30", "limit": Decimal("10000000.00")},
    {"name": "Reliance Jio Infocomm Ltd", "terms": "NET60", "limit": Decimal("25000000.00")},
    {"name": "Bharti Airtel Enterprise Services", "terms": "NET30", "limit": Decimal("18000000.00")},
    {"name": "HCL Technologies Enterprise", "terms": "NET30", "limit": Decimal("11000000.00")},
    {"name": "Larsen & Toubro Infotech", "terms": "NET45", "limit": Decimal("14000000.00")},
    {"name": "Tech Mahindra Global Solutions", "terms": "NET30", "limit": Decimal("9000000.00")},
    {"name": "Mahindra & Mahindra Digital", "terms": "NET45", "limit": Decimal("13000000.00")},
    {"name": "Bajaj Finserv Technology Core", "terms": "NET15", "limit": Decimal("8000000.00")},
    {"name": "ICICI Securities Technology Group", "terms": "NET15", "limit": Decimal("9500000.00")},
    {"name": "HDFC Bank Digital Banking Division", "terms": "NET15", "limit": Decimal("22000000.00")},
    {"name": "Axis Capital Technology Infrastructure", "terms": "NET30", "limit": Decimal("8500000.00")},
    {"name": "Kotak Mahindra Prime Systems", "terms": "NET30", "limit": Decimal("7500000.00")},
    {"name": "State Bank of India Digital Core", "terms": "NET60", "limit": Decimal("30000000.00")},
    {"name": "Adani Ports & Logistics Systems", "terms": "NET45", "limit": Decimal("16000000.00")},
    {"name": "ITC Infotech Global Services", "terms": "NET30", "limit": Decimal("7000000.00")},
    {"name": "Sun Pharma IT Infrastructure", "terms": "NET30", "limit": Decimal("6500000.00")},
    {"name": "Dr Reddys Laboratories Systems", "terms": "NET30", "limit": Decimal("6000000.00")},
    {"name": "Cipla Global Digital Operations", "terms": "NET30", "limit": Decimal("5500000.00")},
    {"name": "Titan Company Digital Platforms", "terms": "NET15", "limit": Decimal("5000000.00")},
    {"name": "Asian Paints Supply Chain Tech", "terms": "NET30", "limit": Decimal("7500000.00")},
    {"name": "Maruti Suzuki IT Infrastructure", "terms": "NET45", "limit": Decimal("12000000.00")},
    {"name": "Tata Motors Fleet Telematics", "terms": "NET45", "limit": Decimal("11000000.00")},
    {"name": "Hero MotoCorp Connected Systems", "terms": "NET30", "limit": Decimal("6500000.00")},
]

# Repeat or expand customer names up to 100 programmatically
def get_accounts_master(count: int) -> List[Dict[str, Any]]:
    """Generate `count` realistic enterprise account dicts."""
    results = []
    base_len = len(ENTERPRISE_CUSTOMERS)
    for i in range(count):
        tpl = ENTERPRISE_CUSTOMERS[i % base_len]
        suffix = f" Div-{i // base_len + 1}" if i >= base_len else ""
        results.append({
            "name": f"{tpl['name']}{suffix}",
            "payment_terms": tpl["terms"],
            "credit_limit": tpl["limit"],
            "currency": "INR",
            "status": "ACTIVE",
        })
    return results
