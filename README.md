# Order-to-Cash (O2C) Revenue Assurance & Revenue Leakage Detection Platform

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18.6-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)

An enterprise-grade, three-tier financial integrity platform that provides complete visibility into the Order-to-Cash (O2C) lifecycle. Built with a deterministic rule-based detection engine, the platform reconciles cross-stage transactional data, detects 12 critical revenue leakage and process violation categories, synthesizes forensic evidence dossiers with expected vs. actual discrepancies, and quantifies financial impact in Indian Rupees (INR).

---

## Application Screenshots

Captured directly from the running production-mode application backed by live PostgreSQL queries:

### 1. Executive Revenue Assurance Overview Dashboard
Real-time operational totals, high-level leakage KPI card in INR, stacked risk severity distributions, active anomaly rule breakdown, and recent flagged exceptions.

![O2C Revenue Assurance Dashboard](docs/images/dashboard-overview.png)

---

### 2. Exception Explorer
Interactive exception registry supporting full-text search across entity IDs and explanations, dynamic severity filtering (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), anomaly classification filters, and direct audit access.

![Exception Explorer](docs/images/exception-explorer.png)

---

### 3. Forensic Exception Detail & Discrepancy Dossier
Deep-dive inspection modal displaying root-cause explanations, recommended business remediations, side-by-side **Expected vs. Actual Discrepancy Analysis**, and structured JSON audit payloads linked to source database records.

![Exception Detail Dossier](docs/images/exception-detail.png)

---

### 4. Commercial Transactional Ledger (Sales Orders)
Unified transactional ledger providing multi-stage operational tracking across customer accounts, commercial values, and state progression.

![Transactional Order Ledger](docs/images/transactions.png)

---

## Table of Contents

1. [The Actual Business Problem](#the-actual-business-problem)
2. [Why Existing O2C Processes Fail](#why-existing-o2c-processes-fail)
3. [Our Business Objective](#our-business-objective)
4. [Solution Approach](#solution-approach)
5. [Complete System Architecture](#complete-system-architecture)
6. [Database Design & Relational Schema](#database-design--relational-schema)
7. [The 12 Anomaly Detection Rules](#the-12-anomaly-detection-rules)
8. [Technology Stack](#technology-stack)
9. [Project Directory Structure](#project-directory-structure)
10. [Complete Windows Setup Guide](#complete-windows-setup-guide)
11. [REST API Reference](#rest-api-reference)
12. [Synthetic Data Generation & Evaluation Protocol](#synthetic-data-generation--evaluation-protocol)
13. [Verified Business Results & Demo Walkthrough](#verified-business-results--demo-walkthrough)
14. [Security & Data Integrity](#security--data-integrity)
15. [Future Roadmap](#future-roadmap)

---

## The Actual Business Problem

The Order-to-Cash (O2C) cycle is the primary financial engine of every commercial enterprise. It spans every operational and commercial touchpoint required to convert customer demand into recognized, collected cash:

$$\text{Account Master} \longrightarrow \text{Quote} \longrightarrow \text{Sales Order} \longrightarrow \text{Fulfillment / Shipment} \longrightarrow \text{Billing Invoice} \longrightarrow \text{Cash Remittance} \longrightarrow \text{Dispute / Reconciliation}$$

In enterprise environments, these stages are rarely executed within a single unified application. Instead, data is fragmented across disparate enterprise systems:
- **CRM & CPQ Systems** manage accounts, pricing catalogs, and quotes.
- **Order Management Systems (OMS)** capture confirmed sales orders and commercial contracts.
- **Warehouse Management Systems (WMS) & 3PL Logistics** manage inventory picking, packing, and fulfillment dispatches.
- **Enterprise Resource Planning (ERP)** generates Accounts Receivable (AR) billing invoices and ledger entries.
- **Treasury Management & Banking Portals** ingest bank lockbox files, wire transfers, and customer payment remittances.
- **Customer Support Portals** track post-billing invoice disputes, quantity rejections, and credit memo requests.

Because these operational boundaries operate on different cadences, data schemas, and transactional batch intervals, **systemic revenue leakage** emerges silently between the seams of the process.

### Real-World Business Failure Modes

1. **Fulfillment vs. Billing Desynchronization (Overbilling & Underbilling):**
   When warehouse stockouts cause partial shipments (e.g., customer ordered 10 units, warehouse shipped 8), billing systems frequently bill for the original order quantity (10 units) rather than actual delivered goods. The customer detects the discrepancy, refuses payment, and enters a prolonged dispute. Conversely, goods shipped without automated billing triggers result in complete unbilled inventory loss.
2. **Duplicate Invoicing & Split Billing:**
   System retries, recurring billing batch errors, or manual re-entry result in duplicate invoice generation for the same sales order line, artificially inflating booked revenue and creating severe accounting inaccuracies.
3. **Payment Allocation Anomalies & Unapplied Cash:**
   Customer remittances arriving via wire or check are frequently applied multiple times to duplicate records, applied in excess of outstanding balances, or left stranded as unallocated cash in suspense accounts.
4. **Premature Order Closure:**
   Sales orders are prematurely marked `CLOSED` in ERP workflows while outstanding invoices remain unpaid, preventing automated collection workflows and writing off viable receivables.
5. **Customer Dispute & AR Disconnect:**
   When customers lodge formal disputes regarding pricing errors or damaged deliveries, the dispute remains isolated within support tickets. Meanwhile, AR systems continue calculating automated aging penalties, issuing dunning notices, or misstating collectible cash.
6. **Short Payments & SLA Aging Breaches:**
   Customers arbitrarily deduct withholding taxes, freight allowances, or disputed amounts without explanation. These small, systemic deductions accumulate across thousands of invoices, resulting in millions in uncollected cash.

---

## Why Existing O2C Processes Fail

Traditional enterprise approaches to revenue assurance consistently fall short due to structural limitations:

| Traditional Approach | Structural Failure Mode | Business Impact |
| :--- | :--- | :--- |
| **Manual Spreadsheet Audits** | Finance teams manually export CSV dumps from ERP, WMS, and CRM into Excel spreadsheets at month-end. | Reconciliations occur 30–45 days after transaction execution; errors are detected long after cash leakage has occurred. |
| **Point-to-Point Batch Integrations** | Nightly ETL cron jobs push state changes between systems without validating cross-entity business invariants. | Silent data truncation, race conditions, and lack of line-item traceability across fulfillment and billing. |
| **Fragmented Audit Logging** | Database tables use mutable `updated_at` overwrite semantics without preserving an append-only event ledger. | Impossible to prove *when* a state transition occurred or reconstruct the state of an order when an invoice was issued. |
| **Generic Anomaly Detection** | "Black-box" unsupervised machine learning models flag statistical outliers without deterministic rule justification. | Finance teams cannot take action because the model cannot explain the contractual discrepancy or generate an audit dossier. |

---

## Our Business Objective

This platform provides an automated, explainable, and deterministic Revenue Assurance platform that:
1. **Unifies the O2C Lifecycle:** Consolidates Accounts, Quotes, Orders, Shipments, Invoices, Payments, and Disputes into a strictly typed, referentially intact relational graph.
2. **Maintains Complete Event Traceability:** Preserves an immutable, append-only `status_events` audit trail for every entity state transition.
3. **Executes 12 Deterministic Detection Rules:** Scans operational records against mathematically proven business invariants without relying on opaque models.
4. **Produces Forensic Evidence Dossiers:** Quantifies exact financial leakage in INR ($\text{₹}$) and generates audit dossiers detailing Expected vs. Actual values.
5. **Guarantees Evaluation Integrity:** Employs an isolated `ground_truth_anomalies` dataset strictly reserved for offline precision/recall benchmarking, completely segregated from detection runtime APIs and frontend interfaces.

---

## Solution Approach

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE O2C ASSURANCE PIPELINE                             │
│                                                                                        │
│  [ Synthetic O2C Generator ]                                                           │
│         │ (Deterministic Seed: 20261022, UUIDv5 Identifiers, Dependency Order)         │
│         ▼                                                                              │
│  [ PostgreSQL 18 Relational Persistence Layer ]                                         │
│    ├── Master Entities (Accounts, Quotes, Orders, Shipments, Invoices, Payments)       │
│    ├── Append-Only Event Ledger (status_events)                                        │
│    └── ISOLATED Ground-Truth Table (ground_truth_anomalies) ◄── [ STRICT ZERO-ACCESS ] │
│         │                                                                              │
│         ▼ (Read-Only Scan of Operational Tables)                                       │
│  [ 12-Rule Deterministic Detection Engine ]                                            │
│    ├── Cross-Entity Invariant Verification                                             │
│    ├── Variance Calculation (Expected Benchmark vs. Recorded Actual)                   │
│    └── Financial Leakage Quantification (INR)                                          │
│         │                                                                              │
│         ▼ (Persists Audit Evidence)                                                    │
│  [ Exception & Evidence Ledger ]                                                       │
│    ├── exception_records (Business ID, Rule, Severity, Leakage, Remediation)           │
│    └── exception_evidence (Source Tables, Conflicting IDs, JSON Payloads)              │
│         │                                                                              │
│         ▼ (FastAPI REST Service Layer)                                                 │
│  [ Executive Dashboard & Exception Explorer UI ]                                       │
│    ├── Live Executive KPI Cards & Severity Stack                                       │
│    ├── 12-Detector Anomaly Breakdown                                                   │
│    └── Interactive Forensic Dossier Modal with Remediation Workflows                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

The platform's operational pipeline enforces four foundational architectural guarantees:
1. **Deterministic Reproducibility:** All synthetic transactional datasets and injected anomalies are generated from a constant pseudo-random seed (`20261022`) using `UUIDv5` hashing. Re-running the generation sequence produces byte-identical databases.
2. **Zero Ground-Truth Contamination:** The detection engine and backend API routers are physically and logically barred from querying `ground_truth_anomalies`. Detection is executed entirely via deterministic SQL queries and business logic evaluated against active operational records.
3. **Explainable Discrepancy Evidence:** Every detected exception generates an associated `exception_evidence` record storing the source table, conflicting document references, expected values, actual values, and discrepancy deltas.
4. **Real-Time Synchronous Execution:** Analysts can trigger an on-demand detection scan via `POST /api/detection/run`, scanning hundreds of thousands of lifecycle records across all 12 rules in sub-second execution times.

---

## Complete System Architecture

### A. Three-Tier Physical Architecture

```mermaid
flowchart TD
    subgraph Presentation_Tier ["Presentation Layer (frontend/)"]
        UI["React 18 + TypeScript + Vite SPA"]
        Sidebar["Enterprise Sidebar Navigation"]
        OverviewView["Overview KPI Dashboard"]
        ExplorerView["Exception Explorer & Filters"]
        DetailModal["Forensic Dossier & Evidence Modal"]
        LedgerView["Transactional Ledgers (Orders, Invoices, etc.)"]
        APIClient["Typed API Client (Fetch + Environment Config)"]
    end

    subgraph Application_Tier ["Application & Logic Layer (backend/)"]
        FastAPIApp["FastAPI REST Application (Uvicorn)"]
        DashboardRouter["/api/dashboard (Executive Summaries)"]
        ExceptionsRouter["/api/exceptions (Explorer & Dossiers)"]
        TransactionsRouter["/api/orders, /api/invoices, etc."]
        DetectionRouter["/api/detection/run (Synchronous Trigger)"]
        HealthRouter["/health, /health/db (System Diagnostics)"]
        
        subgraph Engine_Core ["Detection & Generation Core"]
            Engine["AnomalyDetectionEngine"]
            Detectors["12 Specialized Rule Detectors"]
            Generator["Synthetic O2C Data Generator"]
            Injector["Deterministic Anomaly Injector"]
        end
        
        ORM["SQLAlchemy 2.x ORM & Connection Pool"]
    end

    subgraph Database_Tier ["Database & Persistence Layer (database/)"]
        PG["PostgreSQL 18 Relational Database (o2c_revenue_db)"]
        Migrations["Alembic Migrations (database/migrations/)"]
        Diagnostics["Read-Only Diagnostic Scripts (database/sql/)"]
        SeedDocs["Seed Workflow Documentation (database/seeds/)"]
        
        subgraph Schema_Tables ["Relational Schema"]
            MasterTables[("accounts, quotes, quote_lines")]
            OrderTables[("sales_orders, order_lines")]
            FulfillmentTables[("shipments, shipment_lines")]
            BillingTables[("invoices, invoice_lines")]
            TreasuryTables[("payments, payment_allocations")]
            DisputeTables[("disputes, status_events")]
            ExceptionTables[("exception_records, exception_evidence")]
            GroundTruthTable[("ground_truth_anomalies (Isolated)")]
        end
    end

    UI --> APIClient
    APIClient -->|HTTP / JSON on Port 8000| FastAPIApp
    FastAPIApp --> DashboardRouter & ExceptionsRouter & TransactionsRouter & DetectionRouter & HealthRouter
    DetectionRouter --> Engine
    Engine --> Detectors
    Detectors --> ORM
    DashboardRouter & ExceptionsRouter & TransactionsRouter --> ORM
    ORM -->|Psycopg Driver on Port 5432| PG
    Migrations -.->|Schema Versioning a862bb2a11e5| PG
    Generator -.->|Seeding Sequence| ORM
```

---

### B. Order-to-Cash (O2C) Business Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant Sales as Sales / CPQ
    participant OMS as Order Management
    participant WMS as Warehouse (Fulfillment)
    participant Billing as AR / Billing
    participant Treasury as Cash Management
    participant Engine as RevAssure Detection Engine

    Customer->>Sales: Request commercial quotation
    Sales->>OMS: Quote accepted; Convert to Sales Order (CONFIRMED)
    OMS->>WMS: Issue dispatch order
    WMS->>WMS: Pick, pack, and ship inventory (SHIPPED)
    WMS->>Billing: Transmit shipment fulfillment lines
    Billing->>Billing: Generate Invoice against fulfilled quantities (ISSUED)
    Billing->>Customer: Transmit billing invoice
    Customer->>Treasury: Remit payment via Wire / ACH / Check
    Treasury->>Billing: Ingest remittance; Allocate payment to Invoice (PAID)
    
    Note over Engine: Periodic or Triggered Assurance Scan
    Engine->>WMS: Audit actual shipped quantities
    Engine->>Billing: Audit billed quantities & pricing
    Engine->>Treasury: Audit cash allocations & bank remittances
    Engine->>Engine: Reconcile invariants across all 12 rules
    Engine-->>Billing: Flag Overbilling, Duplicate Invoices, or Unallocated Cash
```

---

### C. Exception Detection & Forensic Evidence Workflow

```mermaid
flowchart LR
    A["Raw Transactional Tables<br/>(Orders, Shipments, Invoices, Payments)"] --> B["12 Rule Detectors"]
    B --> C{"Business Invariant<br/>Violated?"}
    C -- No --> D["Mark Compliant"]
    C -- Yes --> E["Calculate Discrepancy Delta<br/>(Expected vs Actual)"]
    E --> F["Quantify Revenue Leakage (INR)"]
    F --> G["Persist ExceptionRecord"]
    G --> H["Persist ExceptionEvidence<br/>(Source IDs & JSON Payload)"]
    H --> I["Real-Time Executive Dashboard<br/>& Forensic Explorer"]
```

---

## Database Design & Relational Schema

The platform is backed by a relational schema enforced via PostgreSQL foreign keys, composite indexes, and strict decimal arithmetic.

```mermaid
erDiagram
    accounts ||--o{ quotes : "places"
    accounts ||--o{ sales_orders : "contracts"
    accounts ||--o{ invoices : "billed to"
    accounts ||--o{ payments : "remits"
    
    quotes ||--o{ quote_lines : "contains"
    quotes ||--o| sales_orders : "converted to"
    
    sales_orders ||--o{ order_lines : "contains"
    sales_orders ||--o{ shipments : "fulfilled by"
    sales_orders ||--o{ invoices : "billed via"
    
    shipments ||--o{ shipment_lines : "manifests"
    order_lines ||--o{ shipment_lines : "allocates"
    
    invoices ||--o{ invoice_lines : "itemizes"
    shipment_lines ||--o{ invoice_lines : "billed from"
    invoices ||--o{ payment_allocations : "settled by"
    invoices ||--o{ disputes : "disputed by"
    
    payments ||--o{ payment_allocations : "funds"
    
    sales_orders ||--o{ status_events : "lifecycle audit"
    invoices ||--o{ status_events : "lifecycle audit"
    payments ||--o{ status_events : "lifecycle audit"
    
    exception_records ||--o{ exception_evidence : "substantiates"
```

### Relational Entity Specifications

| Table Name | Primary Key | Key Foreign Keys | Purpose & Relational Role |
| :--- | :--- | :--- | :--- |
| `accounts` | `account_id` (UUID) | None | Customer master data holding commercial credit limits and payment terms (e.g., `NET30`). |
| `quotes` | `quote_id` (UUID) | `account_id` | Commercial quotations containing valid-until dates and conversion status. |
| `quote_lines` | `line_id` (UUID) | `quote_id` | Line-item pricing, requested quantities, and approved commercial discounts. |
| `sales_orders` | `order_id` (UUID) | `account_id`, `quote_id` | Confirmed contractual sales orders defining agreed total value and currency. |
| `order_lines` | `line_id` (UUID) | `order_id` | Contracted product quantities, unit prices, and negotiated line discounts. |
| `shipments` | `shipment_id` (UUID) | `order_id` | Physical logistics dispatch notes carrying carrier details and tracking identifiers. |
| `shipment_lines` | `line_id` (UUID) | `shipment_id`, `order_line_id` | Bridge record linking warehouse fulfilled quantities directly to contractual order lines. |
| `invoices` | `invoice_id` (UUID) | `order_id`, `account_id` | Accounts Receivable legal billing documents tracking invoiced, paid, and outstanding balances. |
| `invoice_lines` | `line_id` (UUID) | `invoice_id`, `shipment_line_id` | Invoiced unit prices and line quantities linked directly to delivery fulfillment notes. |
| `payments` | `payment_id` (UUID) | `account_id` | Treasury bank remittances recording amount received, allocated cash, and unallocated balance. |
| `payment_allocations`| `allocation_id` (UUID)| `payment_id`, `invoice_id` | Multi-invoice settlement bridge applying remittance funds against specific invoices. |
| `disputes` | `dispute_id` (UUID) | `invoice_id` | Customer billing claims logging disputed amounts, categorization, and resolution dates. |
| `status_events` | `event_id` (UUID) | Generic `entity_id` | Immutable append-only audit trail logging `from_status` $\rightarrow$ `to_status` transitions with timestamps. |
| `exception_records`| `exception_id` (UUID)| Target `entity_id`, `account_id`| Master table for detected revenue leakage, severity, financial impact, and remediation steps. |
| `exception_evidence`| `evidence_id` (UUID) | `exception_id`, `source_id` | Forensic payload table capturing expected benchmark, actual values, and source audit JSON. |
| `ground_truth_anomalies`| `anomaly_id` (UUID)| Target `entity_id` | Isolated benchmark table populated strictly by generator for offline evaluation metrics. |

---

## The 12 Anomaly Detection Rules

The detection engine evaluates operational records across 12 deterministic rules. Each rule quantifies exact financial exposure without heuristic guesswork:

| # | Detector Rule Code | Business Definition | Detection Logic & Invariant Checked | Financial & Operational Impact |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `OVERBILLING_QUANTITY` | Quantity Billed Exceeds Delivery | $\sum Q_{\text{invoiced}} > \sum Q_{\text{shipped}}$ for an order line item. | Customer rejects invoice; leads to delayed cash collection and forced credit memos. |
| **2** | `OVERBILLING_AMOUNT` | Invoice Price Exceeds Contract | Invoiced unit price or total line amount exceeds approved sales order pricing. | Damaged customer trust, contractual audit breach, and inevitable billing deductions. |
| **3** | `UNDERBILLING` | Shipped Goods Unbilled or Under-Invoiced | $\sum Q_{\text{shipped}} > \sum Q_{\text{invoiced}}$, or invoiced unit price is below contractual price. | **Direct revenue leakage**; physical inventory leaves warehouse without revenue realization. |
| **4** | `DUPLICATE_INVOICE` | Redundant Billing Documents | Multiple active invoices share the identical `order_id`, customer, and total amount within 72 hours. | Artificially inflated Accounts Receivable; customer overpayment followed by complex refund reconciliations. |
| **5** | `DUPLICATE_PAYMENT_ALLOCATION`| Double-Applied Remittance | Multiple allocation records link the same `payment_id` and `invoice_id` with identical settlement amounts. | Distorts customer ledger; falsely marks invoice as paid while leaving real receivables uncollected. |
| **6** | `EXCESSIVE_PAYMENT_ALLOCATION`| Settlement Exceeds Invoice Balance | $\sum \text{Allocations} > \text{Total Invoiced Amount}$. | Creates phantom negative balances and customer credit balances requiring treasury manual intervention. |
| **7** | `PREMATURE_ORDER_CLOSURE` | Closed Order with Unpaid Invoices | Sales order status is `CLOSED`, but associated invoices possess `outstanding_balance > 0`. | Uncollected revenue written off prematurely; automated collection and dunning workflows halted. |
| **8** | `INVALID_STATUS_TRANSITION` | Out-of-Order Lifecycle State | Entity skips required prerequisite states (e.g., Quote $\rightarrow$ Shipped, or Order $\rightarrow$ Paid without Invoice). | Bypasses commercial approvals, credit limit verifications, and SOX compliance controls. |
| **9** | `DISPUTE_AR_DISCONNECT` | Dunning on Disputed Invoices | Active dispute exists on an invoice, but AR continues treating invoice as normal delinquent debt without dispute hold. | Customer frustration, strained business relationships, and legal exposure. |
| **10**| `SHORT_PAYMENT` | Unexplained Underpayment | Customer pays partial amount without an associated dispute, adjustment, or contractual credit memo. | Silent leakage; thousands of unresolved fractional deductions accumulate into substantial losses. |
| **11**| `SLA_AGING_BREACH` | Unacceptable Operational Delay | Order confirmed to shipped, or shipped to invoiced duration exceeds established SLA cutoffs (e.g., > 14 days). | Cash flow velocity deceleration and contractual fulfillment penalty liabilities. |
| **12**| `UNALLOCATED_CASH` | Stranded Bank Remittances | Payment received and verified by bank, but `unallocated_amount > 0` past standard holding periods. | Idle enterprise cash, understated collections, and unnecessary dunning letters to paid customers. |

---

## Technology Stack

### Frontend Presentation Layer
- **Framework:** React 18.3 (TypeScript 5.6)
- **Build Tool:** Vite 5.4 (ES2020 modules, 5.2s cold build)
- **Styling:** Tailwind CSS 3.4 (Enterprise light SaaS design system)
- **Icons:** Lucide React 0.468

### Application & API Layer
- **Framework:** FastAPI 0.110+ (Asynchronous ASGI application)
- **Web Server:** Uvicorn (High-performance ASGI server)
- **Validation:** Pydantic v2 (Strict schema validation and data serialization)
- **ORM:** SQLAlchemy 2.0 (Declarative mapping with connection pooling)
- **Testing:** Pytest 8.4 (21/21 passed automated unit and integration tests)

### Database & Persistence Layer
- **RDBMS Engine:** PostgreSQL 18.6 (Compiled by MSVC 19.44 on Windows x86_64)
- **Database Driver:** Psycopg 3.2 (Binary wheels with native PostgreSQL protocol support)
- **Schema Migration:** Alembic 1.13+ (Decoupled migration tier in `database/migrations/`)

---

## Project Directory Structure

```
o2c-revenue-assurance-platform/
│
├── frontend/                                   # Presentation Layer (React 18 + Vite)
│   ├── src/
│   │   ├── components/                         # UI Components
│   │   │   ├── AnomalyTypeBreakdown.tsx        # 12-Detector visual breakdown cards
│   │   │   ├── ExceptionDetailModal.tsx        # Forensic dossier modal with Expected vs Actual
│   │   │   ├── Header.tsx                      # Top bar with Run Detection & Refresh actions
│   │   │   ├── KpiCard.tsx                     # Enterprise metric KPI cards
│   │   │   ├── Pagination.tsx                  # Standardized data table pagination
│   │   │   ├── SeverityDistribution.tsx        # Horizontal stacked risk severity bar
│   │   │   ├── Sidebar.tsx                     # Core assurance navigation & DB status pill
│   │   │   └── StateFeedback.tsx               # Skeletons, empty states, and error alerts
│   │   ├── pages/                              # Main Application Views
│   │   │   ├── OverviewPage.tsx                # Executive overview dashboard
│   │   │   ├── ExceptionsPage.tsx              # Exception explorer with search & filters
│   │   │   ├── OrdersPage.tsx                  # Sales order ledger
│   │   │   ├── InvoicesPage.tsx                # Accounts receivable invoice ledger
│   │   │   ├── PaymentsPage.tsx                # Treasury cash settlements ledger
│   │   │   └── DisputesPage.tsx                # Customer dispute registry
│   │   ├── services/
│   │   │   └── api.ts                          # Strongly-typed API client
│   │   ├── types/
│   │   │   └── index.ts                        # Shared TypeScript interfaces
│   │   └── utils/
│   │       └── formatters.ts                   # INR currency (₹), date, and badge styling
│   ├── package.json                            # Frontend dependencies & scripts
│   └── vite.config.ts                          # Vite bundler configuration
│
├── backend/                                    # Application & Logic Layer (FastAPI)
│   ├── app/
│   │   ├── api/routes/                         # Modular REST API Endpoints
│   │   │   ├── dashboard.py                    # GET /api/dashboard/summary
│   │   │   ├── exceptions.py                   # GET /api/exceptions, GET /api/exceptions/{id}
│   │   │   ├── transactions.py                 # GET /orders, /invoices, /payments, /disputes
│   │   │   ├── detection.py                    # POST /api/detection/run
│   │   │   └── health.py                       # GET /health, GET /health/db
│   │   ├── core/
│   │   │   └── config.py                       # Pydantic-settings environment configuration
│   │   ├── db/
│   │   │   └── database.py                     # SQLAlchemy engine, SessionLocal, get_db
│   │   ├── detectors/                          # Revenue Leakage Detection Engine
│   │   │   ├── base.py                         # Abstract detector base class & result types
│   │   │   ├── rules.py                        # Implementation of all 12 detection rules
│   │   │   ├── engine.py                       # Detection orchestrator & transaction manager
│   │   │   └── run_detection.py                # Standalone CLI detection runner
│   │   ├── generators/                         # Synthetic Data Generation Pipeline
│   │   │   ├── config.py                       # Generator configurations & distribution specs
│   │   │   ├── base.py                         # Deterministic UUIDv5 generator
│   │   │   ├── anomaly_injector.py             # Realistic edge case injector for 12 rules
│   │   │   └── generate_o2c_data.py            # CLI entrypoint for test & full profiles
│   │   ├── models/                             # Declarative SQLAlchemy 2.x Models
│   │   │   ├── o2c.py                          # 14 Core lifecycle transactional entities
│   │   │   ├── detection.py                    # ExceptionRecord, ExceptionEvidence
│   │   │   └── ground_truth.py                 # GroundTruthAnomaly (Strictly isolated)
│   │   └── schemas/                            # Pydantic v2 Request & Response Schemas
│   ├── tests/                                  # Pytest Automated Test Suite (21 Tests)
│   ├── alembic.ini                             # Points to database/migrations/
│   └── requirements.txt                        # Backend Python dependencies
│
├── database/                                   # Dedicated Database Persistence Tier
│   ├── migrations/                             # Version-Controlled Alembic Migrations
│   │   ├── env.py                              # Migration environment loader
│   │   ├── script.py.mako                      # Migration template
│   │   └── versions/                           # Migration revisions (Head: a862bb2a11e5)
│   ├── seeds/
│   │   └── README.md                           # Seeding guide and profile documentation
│   ├── sql/
│   │   └── diagnostics.sql                     # Safe, read-only SQL diagnostic queries
│   └── README.md                               # Database tier architectural documentation
│
└── docs/                                       # Project Documentation & Screenshot Assets
    ├── images/                                 # Actual application screenshots
    │   ├── dashboard-overview.png
    │   ├── exception-explorer.png
    │   ├── exception-detail.png
    │   └── transactions.png
    ├── PROJECT_REQUIREMENTS.md                 # Primary business requirements specification
    └── SOLUTION_ARCHITECTURE.md                # Detailed technical solution architecture
```

---

## Complete Windows Setup Guide

Follow these exact PowerShell commands to run the platform locally on Windows.

### 1. Prerequisites
- **Python:** 3.11+ installed (Recommended: Python 3.12).
- **Node.js:** 18+ installed (Recommended: Node.js 20 or 22).
- **PostgreSQL:** 15+ installed and running as a Windows service on port `5432`.

### 2. Configure Backend Environment
Navigate to `backend/` and copy the environment template:

```powershell
cd C:\CandidateWorkspace\o2c-revenue-assurance-platform\backend
Copy-Item .env.example .env
```

Ensure `backend/.env` contains your PostgreSQL credentials (URL-encode special characters such as `@` as `%40`):
```env
DATABASE_URL=postgresql+psycopg://postgres:YourSecurePassword@127.0.0.1:5432/o2c_revenue_db
APP_ENV=development
DEBUG=True
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

### 3. Initialize Python Virtual Environment & Install Dependencies
```powershell
# Inside backend/
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Alembic Schema Migrations
Verify that migrations are synchronized to `database/migrations/`:

```powershell
# Inside backend/
.\.venv\Scripts\alembic.exe current
# Expected Output: a862bb2a11e5 (head)

.\.venv\Scripts\alembic.exe history
```

If initializing a fresh database, apply the migrations:
```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

### 5. Start the FastAPI Backend Server
```powershell
# Inside backend/
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend endpoints will be live:*
- Interactive Swagger UI: **http://localhost:8000/docs**
- Raw Health Diagnostic: **http://localhost:8000/health**
- Database Health Check: **http://localhost:8000/health/db**

---

### 6. Configure & Start the React Frontend Server
Open a separate PowerShell terminal:

```powershell
cd C:\CandidateWorkspace\o2c-revenue-assurance-platform\frontend

# Ensure frontend/.env points to backend
Copy-Item .env.example .env

# Install Node modules (if not already installed)
npm install

# Start Vite development server
npm run dev -- --host 0.0.0.0
```
*Frontend UI will be live:*
- Executive Application UI: **http://localhost:5173**

---

## REST API Reference

The backend provides a comprehensive RESTful API mounted under both `/api` and `/api/v1`.

| HTTP Verb | Endpoint | Purpose | Supported Query Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Application status & debug state | None |
| `GET` | `/health/db` | Direct PostgreSQL connectivity verification (`SELECT 1`) | None |
| `GET` | `/api/dashboard/summary` | Executive totals, total leakage in INR, severity & anomaly counts | None |
| `GET` | `/api/exceptions` | Paginated list of detected policy and financial exceptions | `page`, `limit`, `severity`, `anomaly_type`, `entity_type`, `search` |
| `GET` | `/api/exceptions/{id}` | Detailed forensic dossier with Expected vs. Actual and JSON evidence | `exception_id` (UUID Path parameter) |
| `GET` | `/api/orders` | Paginated commercial sales order ledger | `page`, `limit`, `status`, `search` |
| `GET` | `/api/invoices` | Paginated billing invoices with outstanding balances | `page`, `limit`, `status`, `search` |
| `GET` | `/api/payments` | Paginated cash remittances and unallocated balances | `page`, `limit`, `status`, `search` |
| `GET` | `/api/disputes` | Paginated customer billing dispute ledger | `page`, `limit`, `status`, `search` |
| `GET` | `/api/accounts` | Paginated customer master accounts | `page`, `limit`, `search` |
| `POST` | `/api/detection/run` | Synchronously executes all 12 detectors against current DB | None |

---

## Synthetic Data Generation & Evaluation Protocol

### 1. Deterministic Seeding & Identity Strategy
- **Master Seed:** All generators initialize `random.seed(20261022)` and `numpy.random.seed(20261022)`.
- **Deterministic Identifiers:** Primary keys are generated using `UUIDv5` hashing combining a domain namespace constant with business identifiers (e.g., `SO-2026-000001` always yields the exact same UUID).
- **Parent-First Sequence:** Master records are created first (`Accounts` $\rightarrow$ `Quotes`), followed by contractual agreements (`Sales Orders`), fulfillment notes (`Shipments`), invoices, remittances, and disputes.

### 2. Supported Generation Profiles
- **`test` Profile (Active Demo Dataset):**
  - 10 Accounts, 100 Quotes, 70 Sales Orders, 75 Shipments, 83 Invoices, 150 Payments, 5 Disputes, 1,288 Status Events.
  - Generates 36 injected ground-truth anomalies across all 12 categories.
  - Execution time: **0.47 seconds**.
- **`full` Profile (Enterprise Benchmark):**
  - 500 Accounts, 10,000 Quotes, 7,000 Sales Orders, ~8,500 Shipments, ~8,000 Invoices, ~12,000 Payments, ~400 Disputes.
  - Generates ~276,000+ total records and 385 injected anomalies.
  - Execution time: **22.5 seconds**.

### 3. Execution Commands
```powershell
# Inside backend/
# Generate test profile dataset:
.\.venv\Scripts\python.exe -m app.generators.generate_o2c_data --profile test

# Generate full benchmark dataset:
.\.venv\Scripts\python.exe -m app.generators.generate_o2c_data --profile full
```

### 4. Strict Ground-Truth Physical Isolation
The platform establishes a strict architectural boundary between detection and evaluation:
- Injected anomalies are logged to `ground_truth_anomalies`.
- **Zero-Access Guarantee:** No detector in `app/detectors/` and no API route in `app/api/routes/` imports or queries `ground_truth_anomalies`.
- Automated regression tests (`tests/test_detectors.py::test_ground_truth_isolation`) inspect AST imports to guarantee zero code contamination.

---

## Verified Business Results & Demo Walkthrough

### Active Database Verification Metrics
Verified via PostgreSQL read-only diagnostics on the active production database:

| Metric Category | Verified Database Value | Verification Source |
| :--- | :---: | :--- |
| **Customer Accounts** | 10 Master Records | PostgreSQL `accounts` table |
| **Commercial Orders** | 70 Sales Orders | PostgreSQL `sales_orders` table |
| **Billing Invoices** | 83 Invoices | PostgreSQL `invoices` table |
| **Cash Settlements** | 150 Remittances | PostgreSQL `payments` table |
| **Identified Exceptions** | **63 Exceptions** | PostgreSQL `exception_records` table |
| **Total Revenue Leakage** | **₹31,377,824.50 (₹3.14 Cr)** | Sum of `leakage_amount` |
| **Detection Duration** | **0.122 seconds** | Live `POST /api/detection/run` |
| **Severity Breakdown** | 19 Critical, 29 High, 9 Medium, 6 Low | PostgreSQL Group By Query |

### Analyst Investigation Walkthrough

```
Step 1: Executive Triaging
   └─ Analyst observes ₹3.14 Cr in identified leakage on the Overview Dashboard.
   └─ Severity breakdown highlights 19 CRITICAL exceptions requiring immediate remediation.

Step 2: Anomaly Filtering
   └─ Analyst clicks "Overbilling Quantity" on the Anomaly Rule Breakdown chart.
   └─ Exception Explorer loads filtered results showing Invoice INV-2026-000001 (₹96,425.00).

Step 3: Forensic Inspection
   └─ Analyst clicks "View Dossier" to open the deep-dive investigation modal.
   └─ Discrepancy analysis proves: Expected Benchmark = 1.00 unit, Actual Recorded Value = 8.00 units.
   └─ Discrepancy Delta: 7.00 unfulfilled units billed in error.

Step 4: Remediation Action
   └─ Analyst reviews system-recommended action: "Issue Credit Memo for unfulfilled quantity and rebill correct delivered volume."
   └─ Evidence payload confirms delivery note SHP-2026-000001 only dispatched 1 unit from warehouse.
```

---

## Security & Data Integrity

### Implemented Architectural Safeguards
1. **Isolated Database Credentials:** All database credentials are read exclusively through Pydantic `BaseSettings` from local `.env` files. `.env` is globally ignored in `.gitignore`.
2. **SQL Injection Immunity:** 100% of database interactions utilize SQLAlchemy 2.x parameter-bound queries and ORM mappings. No raw string interpolation is permitted.
3. **Foreign Key Integrity:** Database constraints prevent orphan transactional records (e.g., invoices cannot be created without valid sales order references).
4. **Append-Only Event Ledger:** Lifecycle changes are recorded in `status_events` with timestamps, ensuring an untampered audit history.
5. **CORS Security:** Cross-Origin Resource Sharing is locked to authorized frontend origins configured in `settings.cors_origins`.

### Future Enterprise Hardening
- **JWT / OAuth2 Authentication:** Role-Based Access Control (RBAC) partitioning `Analyst`, `Finance Manager`, and `Auditor` personas.
- **TLS In-Transit Encryption:** Strict SSL certificates for PostgreSQL and FastAPI in production containerized clusters.

---

## Future Roadmap

- [ ] **ERP Direct Connectors:** Native ingestion connectors for SAP S/4HANA, Oracle NetSuite, and Salesforce CPQ via Kafka event streaming.
- [ ] **Automated Credit Memo Generation:** One-click integration with ERP billing APIs to automatically draft adjustment credit memos upon exception approval.
- [ ] **Machine Learning Confidence Scoring:** Secondary Bayesian scoring layer that estimates collection probability on long-overdue receivables.
- [ ] **Role-Based Audit Sign-Off:** Digital signatures and dual-custody authorization for marking exceptions as `RESOLVED` or `WAIVED`.

---

## License

This project is licensed under the MIT License — see the LICENSE file for details. Built for enterprise revenue assurance and financial process integrity.
