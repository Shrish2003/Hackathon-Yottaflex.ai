# Synthetic Seed Generation Workflow

This directory documents the synthetic data and seed generation workflow for the Order-to-Cash (O2C) Revenue Assurance Platform.

> **Architecture Principle:**
> Seed orchestration logic resides in the application backend layer (`backend/app/generators/`). The database tier preserves seed documentation, schema rules, and verification standards without duplicating Python generation code.

---

## 1. Generator Architecture

The seed generation pipeline is modularized under `backend/app/generators/`:

- `config.py` — Profile settings (`test` profile vs `full` profile), deterministic random seeds, and distribution parameters.
- `base.py` — Deterministic `UUIDv5` identity generation based on business identifiers and namespace constants.
- `accounts.py` — Customer master data generation (credit limits, payment terms).
- `quotes.py` — Commercial quotes and line-item pricing.
- `orders.py` — Confirmed sales orders, line discounts, and pricing constraints.
- `shipments.py` — Delivery notes, carrier tracking, and line quantities.
- `invoices.py` — Invoiced revenue, tax calculations, and billing schedules.
- `payments.py` — Remittance ingestion, multi-invoice allocations, and unallocated cash.
- `disputes.py` — Billing dispute logging and resolution outcomes.
- `status_events.py` — Chronological lifecycle transition audit trail.
- `anomaly_injector.py` — Realistic anomaly injection across all 12 leakage rules.
- `generate_o2c_data.py` — Orchestrator executing the generation sequence in dependency order.

---

## 2. Profiles: Test vs. Full

1. **`test` Profile (Fast Validation & Demo):**
   - Accounts: 10
   - Quotes: 100
   - Sales Orders: 70
   - Shipments: 75
   - Invoices: 83
   - Payments: 150
   - Disputes: 5
   - Status Events: 1,288
   - Injected Anomalies: 36 (covering all 12 anomaly categories)
   - Runtime: ~0.5 seconds.

2. **`full` Profile (Enterprise Benchmark):**
   - Accounts: 500
   - Quotes: 10,000
   - Sales Orders: 7,000
   - Shipments: ~8,500
   - Invoices: ~8,000
   - Payments: ~12,000
   - Disputes: ~400
   - Records: ~276,000+
   - Injected Anomalies: 385
   - Runtime: ~20-30 seconds.

---

## 3. How to Execute Seed Generation

To populate or regenerate seed data from the backend application tier:

```powershell
cd backend

# For fast test profile:
.\.venv\Scripts\python.exe -m app.generators.generate_o2c_data --profile test

# For full enterprise benchmark profile:
.\.venv\Scripts\python.exe -m app.generators.generate_o2c_data --profile full
```

### Determinism Guarantee
All generation utilizes fixed random seed `20261022` and deterministic UUIDs (`uuid.uuid5(UUID_NAMESPACE, ...)`). Repeated generation on the same profile produces identical primary keys, amounts, and anomaly distributions.
