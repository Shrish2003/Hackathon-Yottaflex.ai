# PROJECT REQUIREMENTS SPECIFICATION
## Order-to-Cash (O2C) Revenue Assurance and Revenue Leakage Detection Platform
**Document Version:** 1.1.0-DISCOVERY  
**Phase:** Project Discovery & Business Requirements Specification  
**Status:** DRAFT FOR STAKEHOLDER & DEVELOPER APPROVAL  
**Project Root:** `C:\CandidateWorkspace\o2c-revenue-assurance-platform`  
**Document Path:** `C:\CandidateWorkspace\o2c-revenue-assurance-platform\docs\PROJECT_REQUIREMENTS.md`  
**Domain:** Enterprise Order-to-Cash (O2C), Financial Operations, Revenue Assurance  

---

## 1. Executive Summary

Enterprise financial integrity and operational efficiency depend fundamentally on the seamless execution of the Order-to-Cash (O2C) lifecycle: **Account → Quote → Sales Order → Shipment/Fulfillment → Invoice → Payment → Dispute**. In high-volume enterprise operations, operational data and financial transactions are distributed across disparate operational siloes (CRM, CPQ, ERP, WMS, Billing, Accounts Receivable, and Customer Support). 

When discrepancies arise across these distributed boundaries—such as invoices issued for unfulfilled goods, duplicate billings, misallocated or phantom payments, skipped lifecycle approvals, or unresolved dispute adjustments—the enterprise suffers severe **revenue leakage**, distorted Accounts Receivable (A/R) aging, audit failures, compliance penalties, and customer churn.

The purpose of this platform is to provide an end-to-end, multi-stage **O2C Revenue Assurance and Revenue Leakage Detection Platform**. The system tracks master and transactional records, enforces relational integrity, validates operational state transitions across decoupled, asynchronous business lifecycles, flags financial anomalies with explainable mathematical and documentary evidence, and objectively evaluates detection efficacy against independently isolated ground truth.

This document serves as the authoritative, definitive Business Requirements Specification (BRS) produced during the **Project Discovery Phase**. In strict conformance with discovery governance, **no application code, database schema, synthetic data, or frontend components have been implemented or altered**. All explicit requirements, proposed technical interpretations, and open business questions requiring developer approval are documented herein.

---

## 2. Business Problem & Context

### 2.1 The O2C Operational Landscape
In a standard enterprise, the commercial cycle spans multiple departments and systems:
1. **Sales & Marketing:** Establishes Accounts and issues customer Quotes with negotiated line-item discounts.
2. **Sales Operations:** Converts accepted quotes into legally binding Sales Orders.
3. **Logistics & Warehousing (WMS):** Fulfills orders via single, multiple, or partial Shipments.
4. **Finance & Billing:** Generates Invoices based on goods/services actually fulfilled.
5. **Treasury & Accounts Receivable (A/R):** Ingests incoming Payments and allocates cash across outstanding Invoices.
6. **Customer Care & Collections:** Manages Disputes arising from damaged goods, pricing mismatches, or delivery delays.
7. **Compliance & Audit:** Monitors historical event logs to ensure segregation of duties and regulatory compliance.

### 2.2 Core Failure Modes & Revenue Leakage Vectors
Because information flows asynchronously across multiple operational boundaries, enterprises routinely suffer from structural anomalies:
- **Phantom Billing / Overbilling:** Generating invoices for quantities that were never shipped or delivered.
- **Underbilling / Margin Erosion:** Invoicing at unit prices lower than quoted/ordered, or failing to invoice fulfilled line items.
- **Duplicate Invoicing:** Issuing multiple invoices for the exact same fulfillment event, leading to artificial revenue inflation and customer disputes.
- **Payment Allocation Anomalies:** 
  - Duplicate payment allocations (applying the same payment record twice).
  - Over-allocation (allocating a cumulative amount exceeding the received payment sum).
  - Unallocated cash (payments received but sitting stranded while corresponding invoices remain marked past-due).
- **Premature Order Closure:** Sales orders marked as `CLOSED` while underlying invoices remain partially or fully unpaid.
- **Lifecycle Sequence Violations:** Invoices created prior to shipment generation, orders confirmed without quote acceptance, or stages skipped without audit trace.
- **Dispute-A/R Disconnect:** Open, validated customer disputes that are not factored into A/R aging reports, causing erroneous collection actions.
- **Operational Bottlenecks / SLAs:** Excessive aging between quote creation, order conversion, fulfillment, billing, and cash collection.

---

## 3. Business Objectives

The business objectives of the platform are codified below:

| Objective ID | Business Objective | Description | Success Metric |
| :--- | :--- | :--- | :--- |
| **OBJ-001** | **End-to-End O2C Traceability** | Reconstruct the complete lineage of any transaction from initial customer Account to final Payment allocation and Dispute resolution. | 100% of transaction paths traceable forward and backward across all stages. |
| **OBJ-002** | **Automated Revenue Leakage Detection** | Detect financial and operational anomalies across billing, fulfillment, payments, and lifecycle transitions using explainable deterministic rules. | Zero unflagged leakage instances within known benchmark scenarios. |
| **OBJ-003** | **Explainable Evidence Generation** | For every detected anomaly, generate an auditable evidence package detailing the exact conflicting records, mathematical delta, and financial impact. | 100% of generated exceptions include structured evidence and source record pointers. |
| **OBJ-004** | **Rigorous Independent Evaluation** | Objectively benchmark detector performance (Precision, Recall, F1 Score) against an isolated, uncorrupted ground-truth dataset. | F1 Score $\ge 0.95$ on baseline synthetic benchmark with zero data leakage. |
| **OBJ-005** | **Reproducible Synthetic Simulation** | Generate enterprise-scale synthetic datasets (10k quotes, 7k orders, 8k invoices, 15k payments) with configurable seeds and deterministic repeatability. | 100% bitwise/checksum reproducibility across consecutive generator runs. |
| **OBJ-006** | **Database-Level Relational Integrity** | Store all transactional, master, and audit records in a relational store (PostgreSQL) enforcing strict foreign keys, check constraints, and non-overwriting event logs. | Zero orphaned records or untracked state mutations. |

---

## 4. Scope and Out-of-Scope Items

### 4.1 In-Scope Items
- **Comprehensive O2C Workflow Tracking:** Modeling of Accounts, Quotes, Quote Lines, Sales Orders, Order Lines, Shipments, Shipment Lines, Invoices, Invoice Lines, Payments, Payment Allocations, Disputes, and Status Events.
- **Relational Data Dictionary:** Full specification of all entities, fields, data types, precision, nullability, uniqueness, foreign keys, and validation rules.
- **Standardized Business Identifiers:** Format compliance for `QTE-2026-000001`, `SO-2026-000001`, `SHP-2026-000001`, `INV-2026-000001`, `PAY-2026-000001`, and `DSP-2026-000001`.
- **Synthetic Data Generator:** Parameterized, deterministic generator producing baseline volumes (10,000 quotes, 7,000 orders, 8,000 invoices, 15,000 payments) with distinct counts for payment allocations and lifecycle status events, plus controlled anomaly injection.
- **Ground-Truth Manifest Generation:** Isolated export of known anomaly labels and expected decisions (`ground_truth.csv`/`json`), physically segregated from detection inputs.
- **Deterministic Anomaly Detectors:** Ten (10) distinct rule-based anomaly detection engines covering overbilling, underbilling, duplicate invoices, duplicate allocations, payment over-allocation, premature closure, lifecycle violations, dispute-A/R disconnects, short payments, and SLA aging delays.
- **Evaluation Engine:** Automated calculation of True Positives (TP), False Positives (FP), False Negatives (FN), Precision, Recall, and F1 Score globally and per anomaly category.
- **Audit & History Preservation:** Append-only status event logging to preserve temporal state transitions without in-place overwrites.

### 4.2 Out-of-Scope Items (Phase 1 / Discovery)
- **Direct ERP/CRM API Integrations:** Live two-way synchronization with Salesforce, SAP S/4HANA, NetSuite, or Workday (data ingested via batch files/relational staging).
- **Automated Banking/Payment Gateway Protocols:** Live ISO 20022, SWIFT MT940, or ACH banking network processing (simulated via structured Payment records).
- **Black-Box Deep Learning / Unsupervised LLM Detectors:** Unexplainable neural network models for core exception detection. All detection must remain deterministic, explainable, and rule-based.
- **Multi-Tenancy & Complex IAM:** Multi-tenant infrastructure isolation and corporate SAML/OAuth SSO (single-tenant relational schema assumed for hackathon baseline).
- **Physical Warehousing Operations:** Barcode scanning, RFID tracking, packing slip printing, or freight carrier routing optimization.

---

## 5. Complete Order-to-Cash (O2C) Workflow & Decoupled Business Lifecycles

### 5.1 Architecture of Decoupled, Multi-Dimensional Lifecycles

In enterprise O2C architectures, transactions do not progress along a single, monolithic, linear status path. Instead, **five orthogonal, asynchronous business lifecycles** evolve concurrently:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          1. ORDER LIFECYCLE (SalesOrder)                          │
│   DRAFT ──► CONFIRMED ──► IN_FULFILLMENT ──► PARTIALLY_FULFILLED ──► FULFILLED   │
│                                                     │                     │       │
│                                                     ▼                     ▼       │
│                                                (Short-Close)            CLOSED    │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ triggers
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                       2. FULFILLMENT LIFECYCLE (Shipment)                         │
│           PENDING ──► DISPATCHED ──► IN_TRANSIT ──► DELIVERED                     │
│                            │                            │                         │
│                            ▼                            ▼                         │
│                          LOST                        RETURNED                     │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ fulfills goods
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         3. BILLING LIFECYCLE (Invoice)                            │
│           DRAFT ──► ISSUED ──► PARTIALLY_PAID ──► PAID                            │
│                       │             │               ▲                             │
│                       ▼             ▼               │                             │
│                     VOIDED     WRITTEN_OFF     (Credit Memo Settled)              │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ demands payment
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│               4. PAYMENT & RECEIVABLES LIFECYCLE (Payment & Allocation)           │
│   Payment:     RECEIVED ──► PARTIALLY_ALLOCATED ──► ALLOCATED                     │
│                   │                                                               │
│                   ▼                                                               │
│                BOUNCED / REFUNDED                                                 │
│   A/R Aging:   CURRENT ──► 1-30 DAYS PAST DUE ──► 31-60 PAST DUE ──► 90+ PAST DUE│
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ customer claim
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                        5. DISPUTE LIFECYCLE (Dispute)                             │
│       LODGED ──► UNDER_INVESTIGATION ──► RESOLVED_ACCEPTED (Credit Memo Issued)   │
│                        │             ──► RESOLVED_REJECTED (Payment Demanded)     │
│                        ▼                                                          │
│                    CANCELLED                                                      │
└───────────────────────────────────────────────────────────────────────────────────┘
```

**Key Architectural Principle:** Each dimension maintains its own state machine. For instance, an Order may be `FULFILLED` while its associated Invoice is `PARTIALLY_PAID`, the customer's Accounts Receivable status is `31-60 DAYS PAST DUE`, and an active Dispute is `UNDER_INVESTIGATION`. Conflating these dimensions into a single status field leads to severe state corruption and audit loss.

---

### 5.2 Detailed Lifecycle Specifications

#### 5.2.1 Stage 1: Account and Quote Lifecycle
- **Customer Account:** Establishes master customer identity, credit terms (e.g., Net 30, Net 60), credit limits, tax identifiers, and contact details.
- **Quote Creation:** A formal commercial proposal issued to an Account, containing one or more Quote Lines.
- **Line Economics:** Each Quote Line captures Product/SKU, requested quantity, list price, agreed discount percentage/amount, and calculated net line amount.
- **Quote States:** `DRAFT` → `SUBMITTED` → `APPROVED` → `ACCEPTED` (or `REJECTED` / `EXPIRED`).
- **Conversion Gate:** Only quotes in `ACCEPTED` status can be converted into Sales Orders.

#### 5.2.2 Stage 2: Sales Order Lifecycle
- **Order Ingestion:** Instantiated upon quote acceptance, inheriting verified customer terms, agreed pricing, discounts, and item specifications.
- **Order Lines:** Map 1:1 or 1:N to Quote Lines, specifying ordered quantities, committed delivery dates, and tax requirements.
- **Order States:** `DRAFT` → `CONFIRMED` → `IN_FULFILLMENT` → `PARTIALLY_FULFILLED` → `FULFILLED` → `CLOSED` (or `CANCELLED`).
- **Closure Boundary:** As detailed in OQ-007, whether `CLOSED` reflects purely operational fulfillment completion or requires complete billing settlement is an open decision pending developer sign-off.

#### 5.2.3 Stage 3: Fulfillment & Shipment Lifecycle
- **Fulfillment Execution:** Warehouse generates one or more Shipment records against an active `CONFIRMED` or `IN_FULFILLMENT` Sales Order.
- **Partial Shipments:** Multiple shipments can fulfill a single Sales Order over time.
- **Shipment Lines:** Detail the exact SKUs and quantities packed and dispatched in each shipment event.
- **Shipment States:** `PENDING` → `DISPATCHED` → `IN_TRANSIT` → `DELIVERED` (or `RETURNED` / `LOST` / `CANCELLED`). Fulfilled quantities are tracked cumulatively against ordered quantities.

#### 5.2.4 Stage 4: Billing & Invoice Lifecycle
- **Billing Event:** Generated by Finance strictly against verified `DELIVERED` (or `DISPATCHED`) fulfilled quantities.
- **Invoice Lines:** Must map directly to underlying Shipment Lines / Order Lines.
- **Reconciliation Check:** Invoiced quantity $\le$ Fulfilled quantity; Invoiced unit price $=$ Ordered unit price.
- **Invoice States:** `DRAFT` → `ISSUED` → `PARTIALLY_PAID` → `PAID` (or `VOIDED` / `WRITTEN_OFF`).

#### 5.2.5 Stage 5: Payment & Receivables Lifecycle
- **Cash Ingestion:** Payment records ingested from remittance slips, bank statements, or wires.
- **Allocation Engine:** Employs a many-to-many bridge (`PaymentAllocation`) to allocate cash:
  - One payment can be split across multiple invoices.
  - Multiple payments can satisfy a single invoice over time.
- **Balance Validation:** Total allocated amount across all invoices $\le$ Total received payment amount. Invoice remaining balance decreases monotonically upon allocation.
- **Payment States:** `RECEIVED` → `PARTIALLY_ALLOCATED` → `ALLOCATED` (or `BOUNCED` / `REFUNDED`).
- **A/R Aging States:** `CURRENT`, `PAST_DUE_1_30`, `PAST_DUE_31_60`, `PAST_DUE_61_90`, `PAST_DUE_90_PLUS`.

#### 5.2.6 Stage 6: Dispute Lifecycle
- **Dispute Lodging:** Customer disputes an invoice or specific invoice lines due to pricing errors, damaged goods, missing items, or delivery delays.
- **A/R Reflection:** Active disputes must be explicitly reflected in Accounts Receivable reporting:
  - Disputed amounts must be isolated from undisputed collections.
  - Aging calculations must account for disputed balances.
- **Dispute States:** `LODGED` → `UNDER_INVESTIGATION` → `RESOLVED_ACCEPTED` / `RESOLVED_REJECTED` / `CANCELLED`.

#### 5.2.7 Stage 7: Lifecycle Audit History
- **Event-Driven Immutability:** Any status change on any core entity triggers an immutable `StatusEvent` record.
- **Event Traceability:** Each event records `entity_type`, `entity_id`, `previous_state`, `new_state`, `transition_timestamp`, `actor_id`, and `reason`.
- **Integrity Enforcement:** Historical status records are strictly append-only; in-place overwrites are forbidden. Invalid or skipped transitions are immediately flagged as audit violations.

---

### 5.3 State Transition Matrix

| Entity | Allowed Initial States | Allowed Next States | Terminal States | Invalid Transition Examples |
| :--- | :--- | :--- | :--- | :--- |
| **Quote** | `DRAFT` | `SUBMITTED` | `EXPIRED`, `REJECTED`, `CONVERTED` | `DRAFT` → `CONVERTED`; `REJECTED` → `ACCEPTED` |
| | `SUBMITTED` | `APPROVED`, `REJECTED` | | |
| | `APPROVED` | `ACCEPTED`, `REJECTED`, `EXPIRED` | | |
| | `ACCEPTED` | `CONVERTED` | | |
| **SalesOrder** | `DRAFT` | `CONFIRMED`, `CANCELLED` | `CLOSED`, `CANCELLED` | `DRAFT` → `FULFILLED`; `CONFIRMED` → `CLOSED` |
| | `CONFIRMED` | `IN_FULFILLMENT`, `CANCELLED` | | |
| | `IN_FULFILLMENT`| `PARTIALLY_FULFILLED`, `FULFILLED`| | |
| | `PARTIALLY_FULFILLED`| `FULFILLED`, `CLOSED` (short-close)| | |
| | `FULFILLED` | `CLOSED` | | |
| **Shipment** | `PENDING` | `DISPATCHED`, `CANCELLED` | `DELIVERED`, `CANCELLED`, `RETURNED` | `PENDING` → `DELIVERED`; `RETURNED` → `DISPATCHED` |
| | `DISPATCHED` | `IN_TRANSIT`, `DELIVERED`, `LOST` | | |
| | `IN_TRANSIT` | `DELIVERED`, `LOST`, `RETURNED` | | |
| **Invoice** | `DRAFT` | `ISSUED`, `VOIDED` | `PAID`, `VOIDED`, `WRITTEN_OFF` | `DRAFT` → `PAID`; `ISSUED` → `PAID` (without allocation) |
| | `ISSUED` | `PARTIALLY_PAID`, `PAID`, `DISPUTED` | | |
| | `PARTIALLY_PAID`| `PAID`, `DISPUTED` | | |
| | `DISPUTED` | `ISSUED`, `PARTIALLY_PAID`, `PAID`, `VOIDED` | | |
| **Payment** | `RECEIVED` | `ALLOCATED`, `PARTIALLY_ALLOCATED`, `BOUNCED` | `ALLOCATED`, `BOUNCED`, `REFUNDED` | `RECEIVED` → `REFUNDED` (without processing); `BOUNCED` → `ALLOCATED` |
| | `PARTIALLY_ALLOCATED` | `ALLOCATED`, `REFUNDED` | | |
| **Dispute** | `LODGED` | `UNDER_INVESTIGATION`, `CANCELLED` | `RESOLVED_ACCEPTED`, `RESOLVED_REJECTED`, `CANCELLED` | `LODGED` → `RESOLVED_ACCEPTED` (skipping investigation) |
| | `UNDER_INVESTIGATION`| `RESOLVED_ACCEPTED`, `RESOLVED_REJECTED` | | |

---

## 6. Functional Requirements

### 6.1 Master Data & Account Management
- **FR-001:** The system shall maintain Customer Accounts with unique business identifiers, corporate legal names, billing addresses, credit limits, payment terms (e.g., `NET30`, `NET60`), and active operational status.
- **FR-002:** The system shall enforce credit limit checks prior to Sales Order confirmation.

### 6.2 Quoting & Commercial Terms
- **FR-003:** The system shall record commercial Quotes associated with an Account, capturing quote creation date, expiration date, currency code, total gross amount, total discount amount, and total net amount.
- **FR-004:** The system shall maintain Quote Line items specifying line number, product/SKU code, quantity, list unit price, discount percentage/amount, and calculated line net amount:
  $$\text{Line Net Amount} = (\text{Quantity} \times \text{List Unit Price}) - \text{Discount Amount}$$
- **FR-005:** The system shall support quote lifecycle states (`DRAFT`, `SUBMITTED`, `APPROVED`, `ACCEPTED`, `REJECTED`, `EXPIRED`, `CONVERTED`) and enforce that only `ACCEPTED` quotes can be converted into Sales Orders.

### 6.3 Sales Order Ingestion & Management
- **FR-006:** The system shall create Sales Orders directly derived from `ACCEPTED` Quotes, maintaining an explicit foreign key reference to the originating Quote ID.
- **FR-007:** The system shall maintain Sales Order Lines corresponding to Quote Lines, preserving agreed quantities, unit prices, and line amounts.
- **FR-008:** The system shall maintain Sales Order header totals derived from the sum of active Order Lines.
- **FR-009:** The system shall validate order closure conditions against outstanding invoice balances.

### 6.4 Fulfillment & Shipment Execution
- **FR-010:** The system shall generate Shipment records associated with a confirmed Sales Order, capturing carrier name, tracking number, dispatch timestamp, and delivery timestamp.
- **FR-011:** The system shall track fulfillment at the line level via `ShipmentLine` entities, recording the exact quantity shipped per Sales Order Line.
- **FR-012:** The system shall support partial fulfillment, permitting multiple independent Shipments against a single Sales Order.
- **FR-013:** The system shall enforce cumulative fulfillment validation: the total fulfilled quantity across all non-cancelled shipments for an order line must not exceed the ordered quantity unless an explicit over-shipment tolerance is configured.

### 6.5 Billing & Invoicing
- **FR-014:** The system shall generate Invoices derived from verified Shipment records and Sales Orders.
- **FR-015:** The system shall record Invoice Lines specifying the line item, invoiced quantity, unit price, tax amount, and net line total.
- **FR-016:** The system shall validate that Invoiced Quantity $\le$ Cumulative Fulfilled Quantity for each order line.
- **FR-017:** The system shall validate that Invoiced Unit Price matches the agreed Sales Order Line Unit Price, flagging any negative discrepancy as Underbilling and positive discrepancy as Overbilling.
- **FR-018:** The system shall identify and flag Duplicate Invoices (invoices referencing identical sales order lines/shipments with overlapping billing periods and amounts).

### 6.6 Payment Processing & Allocation Engine
- **FR-019:** The system shall record incoming Payments, capturing payment reference number, remitting account ID, payment method, received amount, and transaction timestamp.
- **FR-020:** The system shall support many-to-many payment allocations via `PaymentAllocation` bridge records, allowing:
  - A single Payment to be allocated across multiple Invoices.
  - Multiple Payments to be allocated against a single Invoice.
- **FR-021:** The system shall enforce that the sum of all allocations for a given Payment does not exceed the total received payment amount:
  $$\sum \text{Allocated Amount} \le \text{Payment Received Amount}$$
- **FR-022:** The system shall enforce that the sum of all allocations for an Invoice does not exceed the total invoice payable balance:
  $$\sum \text{Allocated Amount} \le \text{Invoice Total Amount}$$
- **FR-023:** The system shall identify Duplicate Payment Allocations (identical payment allocation records applied to the same invoice).

### 6.7 Dispute Management & Receivables Adjustments
- **FR-024:** The system shall record customer Disputes linked to specific Invoices and Invoice Lines, documenting dispute reason code, disputed amount, status, and lodging timestamp.
- **FR-025:** The system shall segregate disputed amounts from active, undisputed Accounts Receivable balances, ensuring financial aging reports accurately display net collectible receivables.
- **FR-026:** The system shall track dispute resolutions (`RESOLVED_ACCEPTED`, `RESOLVED_REJECTED`) and link accepted resolutions to corresponding credit adjustments or invoice adjustments.

### 6.8 Lifecycle State Events & Audit History
- **FR-027:** The system shall capture every state change across Quotes, Sales Orders, Shipments, Invoices, Payments, and Disputes as an immutable `StatusEvent` record.
- **FR-028:** The system shall record the source entity type, entity ID, previous status, new status, change timestamp, triggering actor, and change rationale.
- **FR-029:** The system shall prohibit in-place updates or deletions of historical `StatusEvent` records.

### 6.9 Anomaly Detection & Evidence Generation
- **FR-030:** The system shall execute deterministic anomaly detection routines across all O2C transactions.
- **FR-031:** The system shall record every detected anomaly as an `ExceptionRecord` detailing exception type, affected entity, severity, detection timestamp, root-cause categorization, and recommended corrective action.
- **FR-032:** The system shall attach auditable exception evidence to each exception, establishing direct relational or semi-structured traceability to conflicting source records, expected vs. actual numerical values, and discrepancy deltas.

### 6.10 Evaluation & Benchmarking
- **FR-033:** The system shall ingest ground-truth labels from an isolated source file (`ground_truth.csv`/`json`) that is strictly inaccessible to the detection engine during analysis.
- **FR-034:** The system shall compute True Positives, False Positives, False Negatives, Precision, Recall, and F1 Score globally and grouped by anomaly type.
- **FR-035:** The system shall export evaluation reports in structured CSV, JSON, and markdown formats.

---

## 7. Non-Functional Requirements

### 7.1 Performance & Scalability
- **NFR-001:** The relational database and indexing strategy shall support querying and joining across the baseline synthetic volume (10,000 quotes, 7,000 orders, 8,000 invoices, 15,000 payments) with query response times $< 500\text{ ms}$ for standard transactional lookups.
- **NFR-002:** The batch anomaly detection engine shall complete a full evaluation pass over the entire baseline dataset in $< 30\text{ seconds}$ on standard commodity hardware (4 vCPU, 8 GB RAM).

### 7.2 Data Consistency & ACID Guarantees
- **NFR-003:** All database write operations spanning multi-table updates (e.g., order conversion, payment allocation, status event emission) must execute within ACID transactions with `READ COMMITTED` or `SERIALIZABLE` isolation.
- **NFR-004:** Strict foreign-key constraints with `ON DELETE RESTRICT` shall prevent orphaned child records across all core and supporting tables.

### 7.3 Auditability & Immutability
- **NFR-005:** The audit trail (`StatusEvent` and `AuditLog`) shall be strictly append-only. Database-level permissions or triggers must prevent `UPDATE` and `DELETE` operations on historical audit tables.
- **NFR-006:** All monetary calculations must use exact fixed-point decimal arithmetic (`NUMERIC(15,2)` or `NUMERIC(18,4)`) to eliminate binary floating-point rounding errors.

### 7.4 Explainability & Determinism
- **NFR-007:** Anomaly detection must be 100% deterministic and explainable. Given the identical database snapshot, the detection rules must produce the exact same set of exceptions and evidence payloads on every execution.
- **NFR-008:** The detection engine shall not depend on stochastic machine learning models or black-box LLM prompts for primary exception classification.

### 7.5 Portability & Open Standards
- **NFR-009:** The relational database implementation must be 100% ANSI SQL and PostgreSQL 15+ compatible.
- **NFR-010:** Data export formats must strictly adhere to standardized CSV (RFC 4180) and JSON (RFC 8259) specifications.

---

## 8. Core Entity Descriptions & Relational Architecture

### 8.1 The 11 Core Entities

1. **Account:** The root commercial entity representing customer organizations, establishing billing terms, credit parameters, and master contact details.
2. **Quote:** A formal, time-bound commercial offer submitted to an Account detailing proposed pricing, discounts, and payment terms.
3. **QuoteLine:** Individual itemized product/service entries within a Quote, detailing requested quantities, catalog list prices, agreed discounts, and net amounts.
4. **SalesOrder:** A legally binding commercial agreement converted from an accepted Quote, authorizing fulfillment and billing.
5. **OrderLine:** Specific product lines within a Sales Order, defining promised quantities, unit prices, scheduled fulfillment dates, and line status.
6. **Shipment:** A logistics fulfillment record representing the packing and dispatch of goods against a Sales Order.
7. **Invoice:** A formal demand for payment issued by Finance, billing for fulfilled quantities according to contract terms.
8. **InvoiceLine:** Itemized entries on an Invoice mapping directly to fulfilled goods from shipments and order lines.
9. **Payment:** A financial transaction representing cash or credit received from a customer via wire, ACH, check, or credit card.
10. **Dispute:** A formal claim lodged by a customer questioning the validity, quantity, pricing, or fulfillment status of an Invoice or InvoiceLine.
11. **StatusEvent:** An immutable, timestamped audit log capturing every discrete lifecycle transition across all operational entities.

### 8.2 Supporting Entities & Technical Rationales

To maintain relational integrity, avoid unnormalized data anomalies, and support many-to-many operations, the following seven (7) supporting entities are proposed:

| Supporting Entity | Relational Role | Detailed Rationale & Justification |
| :--- | :--- | :--- |
| **ShipmentLine** | 1:N Child of `Shipment`, N:1 to `OrderLine` | **Why Required:** In standard O2C, shipments can be partial. A Sales Order with 5 distinct OrderLines may be fulfilled across 3 separate shipments, with different items and partial quantities in each. Without `ShipmentLine`, it is mathematically impossible to track which specific order lines and quantities were delivered, making item-level fulfillment reconciliation against `InvoiceLine` impossible. |
| **PaymentAllocation** | Bridge Table (M:N between `Payment` and `Invoice`) | **Why Required:** Payments and Invoices exhibit a Many-to-Many relationship: a single enterprise payment (e.g., a \$50,000 wire) frequently settles multiple outstanding invoices, and conversely, a large capital invoice may be paid across multiple installments. Without `PaymentAllocation`, partial payments, split remittances, and duplicate allocations cannot be modeled or reconciled. |
| **InvoiceAdjustment** | 1:N Child of `Invoice` | **Why Required:** Accounting compliance (GAAP/IFRS) strictly prohibits modifying an issued invoice in place. When disputes are resolved or underbilling/tax errors are corrected, adjustments must be recorded as distinct Credit Memos or Debit Memos. |
| **ExceptionRecord** | Anomaly Output Entity | **Why Required:** Stores detected revenue leakage and operational anomalies identified by the detection engine, decoupling raw operational data from detection findings and enabling workflow management of exceptions. |
| **ExceptionEvidence** | Supporting Evidence Entity | **Why Required:** Provides explainability and auditability. Ensures full traceability from detected anomalies to conflicting operational records (e.g., Invoice #104 vs. Shipment #88), storing expected vs. actual values and calculated deltas. *Storage representation (normalized relational vs. semi-structured JSONB) remains open for architecture sign-off.* |
| **AuditLog** | System-Level Event Entity | **Why Required:** Tracks administrative operations, detection engine execution runs, configuration updates, and synthetic dataset generation runs for end-to-end operational governance. |
| **AppUser** | Security & Actor Master | **Why Required:** Maps system actors (`Sales Rep`, `Finance Analyst`, `Warehouse Clerk`, `Customer`, `System Administrator`) to state transitions and audit events to guarantee segregation of duties. |

---

## 9. Comprehensive Data Requirements & Data Dictionary

### 9.1 Standardized Business Identifier Formats
In strict adherence to project specifications, human-readable business identifiers must follow these exact deterministic formats:

| Entity | Business Identifier Format | Regex Pattern | Example Identifier |
| :--- | :--- | :--- | :--- |
| **Quote** | `QTE-{YYYY}-{SEQ:6}` | `^QTE-\d{4}-\d{6}$` | `QTE-2026-000001` |
| **Sales Order** | `SO-{YYYY}-{SEQ:6}` | `^SO-\d{4}-\d{6}$` | `SO-2026-000001` |
| **Shipment** | `SHP-{YYYY}-{SEQ:6}` | `^SHP-\d{4}-\d{6}$` | `SHP-2026-000001` |
| **Invoice** | `INV-{YYYY}-{SEQ:6}` | `^INV-\d{4}-\d{6}$` | `INV-2026-000001` |
| **Payment** | `PAY-{YYYY}-{SEQ:6}` | `^PAY-\d{4}-\d{6}$` | `PAY-2026-000001` |
| **Dispute** | `DSP-{YYYY}-{SEQ:6}` | `^DSP-\d{4}-\d{6}$` | `DSP-2026-000001` |

---

### 9.2 Complete Data Dictionary (DATA-001 to DATA-018)

#### DATA-001: Account Entity Data Definition
- **Table Name:** `accounts`
- **Primary Key:** `account_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `account_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `account_number`| VARCHAR(32) | NO | Business identifier for customer | `ACC-[0-9]{6}` | - | Unique | Alphanumeric, uppercase |
| `account_name` | VARCHAR(255) | NO | Registered legal corporate name | Text | - | No | Length $\ge 2$ chars |
| `credit_limit` | NUMERIC(15,2)| NO | Maximum approved credit balance | $\ge 0.00$ | USD (\$) | No | Must be non-negative |
| `payment_terms`| VARCHAR(32) | NO | Standard contractual payment terms| `NET15`, `NET30`, `NET45`, `NET60`, `DUE_ON_RECEIPT` | Days | No | Must match approved enum |
| `currency` | VARCHAR(3) | NO | Standard functional currency code | `USD` (Hackathon default) | ISO 4217 | No | 3-character ISO code |
| `status` | VARCHAR(32) | NO | Master account status | `ACTIVE`, `HOLD`, `INACTIVE` | - | No | Default `ACTIVE` |
| `created_at` | TIMESTAMPTZ | NO | Record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |
| `updated_at` | TIMESTAMPTZ | NO | Record modification timestamp | Valid ISO timestamp | UTC | No | $\ge \text{created\_at}$ |

---

#### DATA-002: Quote Entity Data Definition
- **Table Name:** `quotes`
- **Primary Key:** `quote_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `quote_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `business_id` | VARCHAR(32) | NO | Human-readable business identifier | `^QTE-\d{4}-\d{6}$` | - | Unique | Format `QTE-2026-000001` |
| `account_id` | UUID | NO | Foreign key reference to Account | Existing `account_id` | - | No | FK Integrity enforced |
| `status` | VARCHAR(32) | NO | Current quote lifecycle state | `DRAFT`, `SUBMITTED`, `APPROVED`, `ACCEPTED`, `REJECTED`, `EXPIRED`, `CONVERTED` | - | No | State transition enforced |
| `total_gross_amount`| NUMERIC(15,2)| NO | Total value before discounts | $\ge 0.00$ | USD (\$) | No | Sum of line gross amounts |
| `total_discount_amount`| NUMERIC(15,2)| NO | Total discounted value | $\ge 0.00$ | USD (\$) | No | Sum of line discount amounts |
| `total_net_amount`| NUMERIC(15,2)| NO | Net quote value after discounts | $\ge 0.00$ | USD (\$) | No | Must equal Gross - Discount |
| `valid_from` | TIMESTAMPTZ | NO | Quote effective date | Valid ISO timestamp | UTC | No | Start of validity |
| `valid_to` | TIMESTAMPTZ | NO | Quote expiration date | Valid ISO timestamp | UTC | No | Must be $>$ `valid_from` |
| `created_at` | TIMESTAMPTZ | NO | Timestamp when quote was drafted | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-003: QuoteLine Entity Data Definition
- **Table Name:** `quote_lines`
- **Primary Key:** `quote_line_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `quote_line_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `quote_id` | UUID | NO | Foreign key reference to Quote | Existing `quote_id` | - | No | FK Integrity enforced |
| `line_number` | INTEGER | NO | Sequential line index within quote | $1, 2, 3, \dots$ | Index | Unique per `quote_id` | Must be $\ge 1$ |
| `product_sku` | VARCHAR(64) | NO | Standard product catalog code | Alphanumeric | - | No | Catalog reference |
| `quantity` | NUMERIC(12,4)| NO | Quoted quantity | $> 0.0000$ | Units (EA) | No | Must be strictly positive |
| `unit_list_price`| NUMERIC(15,2)| NO | Standard catalog list price | $\ge 0.00$ | USD (\$) | No | Non-negative |
| `discount_pct` | NUMERIC(5,2) | NO | Negotiated discount percentage | $0.00 \dots 100.00$ | Percentage | No | Between 0.00 and 100.00 |
| `discount_amount`| NUMERIC(15,2)| NO | Monetary discount applied | $\ge 0.00$ | USD (\$) | No | $(\text{Qty} \times \text{Price}) \times (\text{Pct}/100)$ |
| `line_net_amount`| NUMERIC(15,2)| NO | Calculated net line total | $\ge 0.00$ | USD (\$) | No | $(\text{Qty} \times \text{Price}) - \text{Discount}$ |

---

#### DATA-004: SalesOrder Entity Data Definition
- **Table Name:** `sales_orders`
- **Primary Key:** `order_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `business_id` | VARCHAR(32) | NO | Human-readable business identifier | `^SO-\d{4}-\d{6}$` | - | Unique | Format `SO-2026-000001` |
| `quote_id` | UUID | NO | Foreign key reference to Quote | Existing `quote_id` | - | Unique | Must link to `ACCEPTED` Quote |
| `account_id` | UUID | NO | Foreign key reference to Account | Existing `account_id` | - | No | Must match Quote's `account_id` |
| `status` | VARCHAR(32) | NO | Current order lifecycle state | `DRAFT`, `CONFIRMED`, `IN_FULFILLMENT`, `PARTIALLY_FULFILLED`, `FULFILLED`, `CLOSED`, `CANCELLED` | - | No | State transitions enforced |
| `total_order_value`| NUMERIC(15,2)| NO | Total financial value of order | $\ge 0.00$ | USD (\$) | No | Sum of line totals |
| `order_date` | TIMESTAMPTZ | NO | Date order was confirmed | Valid ISO timestamp | UTC | No | Must be $\ge$ Quote `created_at` |
| `created_at` | TIMESTAMPTZ | NO | Order record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-005: OrderLine Entity Data Definition
- **Table Name:** `order_lines`
- **Primary Key:** `order_line_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_line_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `order_id` | UUID | NO | Foreign key reference to SalesOrder| Existing `order_id` | - | No | FK Integrity enforced |
| `quote_line_id` | UUID | NO | Foreign key reference to QuoteLine | Existing `quote_line_id` | - | Unique per `order_id`| 1:1 line provenance |
| `line_number` | INTEGER | NO | Sequential line index within order | $1, 2, 3, \dots$ | Index | Unique per `order_id` | Must be $\ge 1$ |
| `product_sku` | VARCHAR(64) | NO | Standard product catalog code | Alphanumeric | - | No | Inherited from QuoteLine |
| `ordered_quantity`| NUMERIC(12,4)| NO| Committed order quantity | $> 0.0000$ | Units (EA) | No | Must be strictly positive |
| `unit_price` | NUMERIC(15,2)| NO | Contracted net unit price | $\ge 0.00$ | USD (\$) | No | Inherited from QuoteLine |
| `line_total_amount`| NUMERIC(15,2)| NO| Net line total | $\ge 0.00$ | USD (\$) | No | Ordered Qty $\times$ Unit Price |
| `status` | VARCHAR(32) | NO | Order line fulfillment state | `PENDING`, `PARTIALLY_FULFILLED`, `FULFILLED`, `CANCELLED` | - | No | Default `PENDING` |

---

#### DATA-006: Shipment Entity Data Definition
- **Table Name:** `shipments`
- **Primary Key:** `shipment_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `shipment_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `business_id` | VARCHAR(32) | NO | Human-readable business identifier | `^SHP-\d{4}-\d{6}$` | - | Unique | Format `SHP-2026-000001` |
| `order_id` | UUID | NO | Foreign key reference to SalesOrder| Existing `order_id` | - | No | Order must be `CONFIRMED`/`IN_FULFILLMENT` |
| `carrier` | VARCHAR(64) | NO | Logistics freight carrier | `FEDEX`, `UPS`, `DHL`, `FREIGHT_LINE` | - | No | Standard carrier enum |
| `tracking_number`| VARCHAR(128)| NO | Carrier tracking code | Alphanumeric | - | No | Carrier specific |
| `status` | VARCHAR(32) | NO | Shipment status | `PENDING`, `DISPATCHED`, `IN_TRANSIT`, `DELIVERED`, `RETURNED`, `LOST`, `CANCELLED` | - | No | State transitions enforced |
| `dispatched_at`| TIMESTAMPTZ | YES| Timestamp goods left warehouse | Valid ISO timestamp | UTC | No | Must be $\ge$ Order `order_date` |
| `delivered_at` | TIMESTAMPTZ | YES| Timestamp goods reached customer | Valid ISO timestamp | UTC | No | Must be $\ge$ `dispatched_at` |
| `created_at` | TIMESTAMPTZ | NO | Record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-007: ShipmentLine Entity Data Definition
- **Table Name:** `shipment_lines`
- **Primary Key:** `shipment_line_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `shipment_line_id`| UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `shipment_id` | UUID | NO | Foreign key reference to Shipment | Existing `shipment_id` | - | No | FK Integrity enforced |
| `order_line_id` | UUID | NO | Foreign key reference to OrderLine | Existing `order_line_id`| - | No | OrderLine must belong to Shipment's `order_id` |
| `shipped_quantity`| NUMERIC(12,4)| NO| Actual physical quantity shipped | $> 0.0000$ | Units (EA) | No | Must be strictly positive |
| `created_at` | TIMESTAMPTZ | NO | Record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-008: Invoice Entity Data Definition
- **Table Name:** `invoices`
- **Primary Key:** `invoice_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `invoice_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `business_id` | VARCHAR(32) | NO | Human-readable business identifier | `^INV-\d{4}-\d{6}$` | - | Unique | Format `INV-2026-000001` |
| `order_id` | UUID | NO | Foreign key reference to SalesOrder| Existing `order_id` | - | No | Order must have active shipments |
| `account_id` | UUID | NO | Foreign key reference to Account | Existing `account_id` | - | No | Must match Order's `account_id` |
| `shipment_id` | UUID | YES| Optional direct link to Shipment | Existing `shipment_id` | - | No | Required for shipment-level billing |
| `status` | VARCHAR(32) | NO | Current invoice lifecycle state | `DRAFT`, `ISSUED`, `PARTIALLY_PAID`, `PAID`, `DISPUTED`, `VOIDED`, `WRITTEN_OFF` | - | No | State transitions enforced |
| `total_invoiced_amount`| NUMERIC(15,2)| NO| Gross invoice balance payable | $\ge 0.00$ | USD (\$) | No | Sum of invoice line amounts |
| `paid_amount` | NUMERIC(15,2)| NO | Cumulative settled amount | $\ge 0.00$ | USD (\$) | No | Derived from PaymentAllocations |
| `outstanding_balance`| NUMERIC(15,2)| NO| Remaining collectible balance | $\ge 0.00$ | USD (\$) | No | Must equal Total - Paid |
| `issue_date` | TIMESTAMPTZ | NO | Date invoice was published | Valid ISO timestamp | UTC | No | Must be $\ge$ Shipment date |
| `due_date` | TIMESTAMPTZ | NO | Payment due date per terms | Valid ISO timestamp | UTC | No | Must be $\ge$ `issue_date` |
| `created_at` | TIMESTAMPTZ | NO | Record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-009: InvoiceLine Entity Data Definition
- **Table Name:** `invoice_lines`
- **Primary Key:** `invoice_line_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `invoice_line_id`| UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `invoice_id` | UUID | NO | Foreign key reference to Invoice | Existing `invoice_id` | - | No | FK Integrity enforced |
| `order_line_id` | UUID | NO | Foreign key reference to OrderLine | Existing `order_line_id`| - | No | Provenance to contracted item |
| `line_number` | INTEGER | NO | Sequential line index on invoice | $1, 2, 3, \dots$ | Index | Unique per `invoice_id` | Must be $\ge 1$ |
| `invoiced_quantity`| NUMERIC(12,4)| NO| Quantity billed on this line | $> 0.0000$ | Units (EA) | No | Must be strictly positive |
| `unit_price` | NUMERIC(15,2)| NO | Unit price billed | $\ge 0.00$ | USD (\$) | No | Must match OrderLine unit price |
| `line_total_amount`| NUMERIC(15,2)| NO| Invoiced line amount | $\ge 0.00$ | USD (\$) | No | Invoiced Qty $\times$ Unit Price |

---

#### DATA-010: Payment Entity Data Definition
- **Table Name:** `payments`
- **Primary Key:** `payment_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `payment_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `business_id` | VARCHAR(32) | NO | Human-readable business identifier | `^PAY-\d{4}-\d{6}$` | - | Unique | Format `PAY-2026-000001` |
| `account_id` | UUID | NO | Foreign key reference to Account | Existing `account_id` | - | No | Remitting customer account |
| `payment_method`| VARCHAR(32) | NO | Banking transaction channel | `ACH`, `WIRE`, `CHECK`, `CREDIT_CARD` | - | No | Approved payment method enum |
| `payment_reference`| VARCHAR(128)| NO | External bank transaction reference| Alphanumeric | - | No | External reference |
| `amount_received`| NUMERIC(15,2)| NO| Gross cash amount received | $> 0.00$ | USD (\$) | No | Must be strictly positive |
| `amount_allocated`| NUMERIC(15,2)| NO| Amount allocated to invoices | $\ge 0.00$ | USD (\$) | No | Sum of allocations |
| `unallocated_amount`| NUMERIC(15,2)| NO| Residual unallocated cash | $\ge 0.00$ | USD (\$) | No | Received - Allocated |
| `status` | VARCHAR(32) | NO | Payment lifecycle status | `RECEIVED`, `PARTIALLY_ALLOCATED`, `ALLOCATED`, `REFUNDED`, `BOUNCED` | - | No | State transitions enforced |
| `payment_date` | TIMESTAMPTZ | NO | Date cash cleared bank | Valid ISO timestamp | UTC | No | Must be $\le \text{CURRENT\_TIMESTAMP}$ |
| `created_at` | TIMESTAMPTZ | NO | Record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-011: PaymentAllocation Entity Data Definition
- **Table Name:** `payment_allocations`
- **Primary Key:** `allocation_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `allocation_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `payment_id` | UUID | NO | Foreign key reference to Payment | Existing `payment_id` | - | No | FK Integrity enforced |
| `invoice_id` | UUID | NO | Foreign key reference to Invoice | Existing `invoice_id` | - | No | FK Integrity enforced |
| `allocated_amount`| NUMERIC(15,2)| NO| Specific cash amount applied | $> 0.00$ | USD (\$) | No | Must be strictly positive |
| `allocation_date`| TIMESTAMPTZ | NO | Date allocation was applied | Valid ISO timestamp | UTC | No | Must be $\ge$ Payment `payment_date` |
| `status` | VARCHAR(32) | NO | Allocation record state | `ACTIVE`, `REVERSED` | - | No | Default `ACTIVE` |
| `created_at` | TIMESTAMPTZ | NO | Record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-012: Dispute Entity Data Definition
- **Table Name:** `disputes`
- **Primary Key:** `dispute_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dispute_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `business_id` | VARCHAR(32) | NO | Human-readable business identifier | `^DSP-\d{4}-\d{6}$` | - | Unique | Format `DSP-2026-000001` |
| `invoice_id` | UUID | NO | Foreign key reference to Invoice | Existing `invoice_id` | - | No | Target disputed invoice |
| `dispute_reason` | VARCHAR(64) | NO | Standardized business dispute code | `DAMAGED_GOODS`, `PRICE_DISCREPANCY`, `MISSING_QUANTITY`, `DELIVERY_DELAY`, `INCORRECT_ITEM` | - | No | Approved enum |
| `disputed_amount`| NUMERIC(15,2)| NO| Amount in legal dispute | $> 0.00$ | USD (\$) | No | Must be $\le$ Invoice balance |
| `status` | VARCHAR(32) | NO | Dispute lifecycle state | `LODGED`, `UNDER_INVESTIGATION`, `RESOLVED_ACCEPTED`, `RESOLVED_REJECTED`, `CANCELLED` | - | No | State transitions enforced |
| `lodged_at` | TIMESTAMPTZ | NO | Timestamp customer opened claim | Valid ISO timestamp | UTC | No | Must be $\ge$ Invoice `issue_date` |
| `resolved_at` | TIMESTAMPTZ | YES| Timestamp dispute was concluded | Valid ISO timestamp | UTC | No | Must be $\ge$ `lodged_at` |
| `created_at` | TIMESTAMPTZ | NO | Record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-013: StatusEvent Entity Data Definition
- **Table Name:** `status_events`
- **Primary Key:** `event_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `entity_type` | VARCHAR(32) | NO | Name of entity undergoing state change| `Quote`, `SalesOrder`, `Shipment`, `Invoice`, `Payment`, `Dispute` | - | No | Core entity name |
| `entity_id` | UUID | NO | Surrogate primary key of target row | Existing UUID | - | No | Dynamic foreign key |
| `business_id` | VARCHAR(32) | NO | Human-readable ID of target row | Formatted Business ID | - | No | Format matching target entity |
| `previous_state`| VARCHAR(32) | YES| Originating lifecycle state | Allowed state enum | - | No | Nullable only on initial creation |
| `new_state` | VARCHAR(32) | NO | Resulting lifecycle state | Allowed state enum | - | No | Valid state for entity |
| `event_timestamp`| TIMESTAMPTZ | NO| Exact time transition occurred | Valid ISO timestamp | UTC | No | Must be chronologically monotonic |
| `actor_id` | UUID | YES| User or system process triggering event| Existing `user_id` or system UUID | - | No | Audit accountability |
| `reason` | TEXT | YES| Business justification or trigger code | Text | - | No | Optional audit comment |

---

#### DATA-014: InvoiceAdjustment Entity Data Definition
- **Table Name:** `invoice_adjustments`
- **Primary Key:** `adjustment_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `adjustment_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `invoice_id` | UUID | NO | Foreign key reference to Invoice | Existing `invoice_id` | - | No | FK Integrity enforced |
| `dispute_id` | UUID | YES| Optional link to resolved Dispute | Existing `dispute_id` | - | No | FK Integrity enforced |
| `adjustment_type`| VARCHAR(32) | NO | Financial adjustment classification | `CREDIT_MEMO`, `DEBIT_MEMO`, `WRITE_OFF`, `TAX_CORRECTION` | - | No | Approved enum |
| `adjustment_amount`| NUMERIC(15,2)| NO| Amount adjusted | $> 0.00$ | USD (\$) | No | Must be positive |
| `reason` | TEXT | NO | Detailed audit justification | Text | - | No | Mandatory description |
| `created_at` | TIMESTAMPTZ | NO | Record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-015: ExceptionRecord Entity Data Definition
- **Table Name:** `exception_records`
- **Primary Key:** `exception_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `exception_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `issue_type` | VARCHAR(64) | NO | Standardized anomaly code | `OVERBILLING_QUANTITY`, `OVERBILLING_AMOUNT`, `UNDERBILLING`, `DUPLICATE_INVOICE`, `DUPLICATE_PAYMENT_ALLOCATION`, `EXCESSIVE_PAYMENT_ALLOCATION`, `PREMATURE_ORDER_CLOSURE`, `INVALID_STATUS_TRANSITION`, `DISPUTE_AR_DISCONNECT`, `SHORT_PAYMENT`, `SLA_AGING_BREACH` | - | No | Must match detected category |
| `entity_type` | VARCHAR(32) | NO | Primary affected entity type | `Invoice`, `PaymentAllocation`, `SalesOrder`, `StatusEvent`, `Dispute` | - | No | Core entity name |
| `entity_id` | UUID | NO | Primary affected surrogate ID | Existing UUID | - | No | Foreign key target |
| `business_id` | VARCHAR(32) | NO | Primary affected business ID | Formatted Business ID | - | No | Standard format |
| `severity` | VARCHAR(16) | NO | Operational risk / financial severity | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO` | - | No | Standard severity enum |
| `detection_timestamp`| TIMESTAMPTZ| NO| Time anomaly was identified | Valid ISO timestamp | UTC | No | Run timestamp |
| `leakage_amount`| NUMERIC(15,2)| YES| Quantified financial leakage impact | $\ge 0.00$ | USD (\$) | No | Optional where applicable |
| `explanation` | TEXT | NO | Plain English root-cause explanation | Text | - | No | Meaningful narrative |
| `recommended_action`| TEXT | NO | Suggested operational remediation | Text | - | No | Meaningful action |

---

#### DATA-016: ExceptionEvidence Entity Data Definition
- **Table Name:** `exception_evidence`
- **Primary Key:** `evidence_id` (UUID / Surrogate)
- **Note:** Relational storage model; physical storage (normalized relational vs. semi-structured JSONB) subject to architecture approval.

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `evidence_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `exception_id` | UUID | NO | Foreign key reference to Exception | Existing `exception_id` | - | No | FK Integrity enforced |
| `evidence_type` | VARCHAR(64) | NO | Type of evidence payload | `MATHEMATICAL_DISCREPANCY`, `TIMELINE_VIOLATION`, `UNFULFILLED_LINE_ITEM`, `DUPLICATE_RECORD_MATCH`, `UNRESOLVED_DISPUTE_BALANCE` | - | No | Approved enum |
| `source_table` | VARCHAR(64) | NO | Primary source database table | Table name string | - | No | Valid table name |
| `source_id` | UUID | NO | Primary source row ID | Existing UUID | - | No | Traceable pointer |
| `conflicting_source_table`| VARCHAR(64)| YES| Secondary conflicting table name | Table name string | - | No | Valid table name |
| `conflicting_source_id`| UUID | YES| Secondary conflicting row ID | Existing UUID | - | No | Traceable pointer |
| `evidence_payload`| JSONB / TEXT| NO | Structured evidence details | Valid JSON / structured text | - | No | Must contain `expected`, `actual`, `delta` |
| `created_at` | TIMESTAMPTZ | NO | Record creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-017: AuditLog Entity Data Definition
- **Table Name:** `audit_logs`
- **Primary Key:** `log_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `log_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `action_type` | VARCHAR(64) | NO | Classification of system action | `DATA_GENERATION`, `ANOMALY_RUN`, `CONFIG_UPDATE`, `EVALUATION_RUN` | - | No | System action enum |
| `actor_name` | VARCHAR(64) | NO | Name of actor or system service | Text | - | No | Non-empty string |
| `details` | JSONB / TEXT| NO | Contextual parameters and summary | Valid JSON / structured text | - | No | Context detail |
| `logged_at` | TIMESTAMPTZ | NO | Timestamp action executed | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

#### DATA-018: AppUser Entity Data Definition
- **Table Name:** `app_users`
- **Primary Key:** `user_id` (UUID / Surrogate)

| Field Name | Physical Type | Nullable | Description | Allowed Values / Enums | Units | Uniqueness | Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `user_id` | UUID | NO | Unique surrogate primary key | Valid UUIDv4 | - | PK (Unique) | System generated |
| `username` | VARCHAR(64) | NO | Unique login / operator identifier | Alphanumeric | - | Unique | Min 3 chars |
| `full_name` | VARCHAR(128)| NO | User's legal name | Text | - | No | Min 2 chars |
| `role` | VARCHAR(32) | NO | Functional persona role | `SALES_REP`, `SALES_OPS`, `WAREHOUSE_CLERK`, `FINANCE_ANALYST`, `SUPPORT_AGENT`, `SYS_ADMIN` | - | No | Approved role enum |
| `is_active` | BOOLEAN | NO | User account state | `TRUE`, `FALSE` | - | No | Default `TRUE` |
| `created_at` | TIMESTAMPTZ | NO | Account creation timestamp | Valid ISO timestamp | UTC | No | $\le \text{CURRENT\_TIMESTAMP}$ |

---

## 10. Synthetic Data Requirements & Distinct Volume Registers

### 10.1 Distinct Volume Registers & Ambiguity Clarification

In compliance with explicit developer feedback, the platform maintains **strictly separated, distinct counts** across all core and supporting transactional records:

| Entity / Dimension | Distinct Target Volume | Relational Role & Distinction |
| :--- | :--- | :--- |
| **Quotes** | **10,000** distinct records | Root commercial proposals issued to Accounts. |
| **Sales Orders** | **7,000** distinct records | Converted from accepted quotes (70% conversion rate). |
| **Shipments** | **7,500** distinct records | Fulfillment dispatches (reflects partial shipments). |
| **Invoices** | **8,000** distinct records | Billing demands issued against delivered goods. |
| **Payments** | **15,000** distinct records | **Mandated discrete Payment entities** (bank cash receipts). |
| **Payment Allocations** | **18,000 - 22,000** records | **Distinct bridge table rows** mapping Payments to Invoices (N:M). |
| **Status Events** | **80,000+** records | **Distinct lifecycle transition event logs** across all entities. |
| **Disputes** | **400 - 600** records | Formal invoice disputes lodged by customers. |

> **Documented Volume Ambiguity:**  
> The original problem statement referenced both *"15,000 payments/events"* and *"15,000 payments"*. In our relational architecture, Payments, Payment Allocations, and Status Events represent three fundamentally distinct structural layers. We strictly preserve the target volume of **15,000 discrete Payment records**, while treating `PaymentAllocation` records (the M:N bridge instances) and `StatusEvent` records (the append-only audit trail) as distinct dependent record counts. Final confirmation on whether the 15,000 count applies strictly to Payments or combined allocation events is registered in **OQ-009**.

### 10.2 Generation Governance & Technical Rules
- **SYN-001 (Configurable Determinism):** Generation must use a single master pseudo-random seed (default: `20261022`). All sub-generators (accounts, quotes, orders, shipments, invoices, payments) must derive deterministic seeds from this master seed.
- **SYN-002 (Bitwise Reproducibility):** Two consecutive generation runs executed with the identical master seed and scaling parameter must produce identical records, identical primary keys, identical business identifiers, and identical file checksums (SHA-256).
- **SYN-003 (Topological Dependency Sorting):** Generation must strictly follow a directed acyclic dependency order:
  $$\text{Accounts} \rightarrow \text{Quotes} \rightarrow \text{QuoteLines} \rightarrow \text{SalesOrders} \rightarrow \text{OrderLines} \rightarrow \text{Shipments} \rightarrow \text{ShipmentLines} \rightarrow \text{Invoices} \rightarrow \text{InvoiceLines} \rightarrow \text{Payments} \rightarrow \text{PaymentAllocations} \rightarrow \text{Disputes}$$
- **SYN-004 (Derived Financial Calculations):** Financial totals must never be independently synthesized. Header gross, discount, and net totals must be strictly derived by aggregating underlying line-item computations.
- **SYN-005 (Chronological Monotonicity):** For any transaction path, record timestamps must be strictly ordered across lifecycle stages:
  $$\text{Quote.created\_at} \le \text{Order.order\_date} \le \text{Shipment.dispatched\_at} \le \text{Shipment.delivered\_at} \le \text{Invoice.issue\_date} \le \text{Payment.payment\_date}$$
- **SYN-006 (Strict Ground-Truth Isolation):** The generator must produce a standalone `ground_truth.csv` and `ground_truth.json` manifest capturing every injected anomaly. The ground-truth manifest must be completely physically isolated from the input transactional datasets ingested by the detection engine.
- **SYN-007 (Export Formats):** The generator must output complete dataset packages including CSV files (RFC 4180), JSON dumps (RFC 8259), SQL seed scripts, a manifest file detailing record counts and checksums, and a validation summary report.

---

## 11. Anomaly Requirements & Edge-Case Coverage

The system must support explicit, controlled simulation and detection for the ten (10) mandated business anomalies:

| Anomaly ID | Issue Type Name | Business Definition & Description | Injected Ground-Truth Mechanism |
| :--- | :--- | :--- | :--- |
| **ANOM-001** | `OVERBILLING_QUANTITY` | Invoice line quantity strictly exceeds the actual delivered/fulfilled quantity recorded on ShipmentLines. | An invoice line is generated with $\text{invoiced\_qty} = \text{fulfilled\_qty} + K$ ($K \ge 1$), or an invoice is generated for an order line with 0 shipments. |
| **ANOM-002** | `OVERBILLING_AMOUNT` | Invoiced unit price or extended line amount exceeds the contracted price on the approved SalesOrderLine. | Invoiced unit price is artificially set higher than the contracted unit price ($\Delta \ge \$1.00$). |
| **ANOM-003** | `UNDERBILLING` | Invoiced unit price is lower than the contracted price, or fulfilled quantities are billed at a discounted/omitted amount, causing revenue loss. | Invoiced unit price is set $< \text{contracted unit price}$, or an invoice omits delivered shipment lines. |
| **ANOM-004** | `DUPLICATE_INVOICE` | Multiple active invoices are generated for the exact same Sales Order / fulfillment event. | Two distinct invoices (`INV-A` and `INV-B`) are created for the same `order_id` with identical line items, quantities, and dates. |
| **ANOM-005** | `DUPLICATE_PAYMENT_ALLOCATION` | The exact same payment allocation record is inserted twice, allocating cash twice to the same invoice from the same payment. | Duplicate row in `payment_allocations` referencing identical `payment_id` and `invoice_id`. |
| **ANOM-006** | `EXCESSIVE_PAYMENT_ALLOCATION` | The cumulative cash allocated across invoices from a payment exceeds the total received payment amount. | Multiple `payment_allocations` created such that $\sum \text{allocated\_amount} > \text{payment.amount\_received}$. |
| **ANOM-007** | `PREMATURE_ORDER_CLOSURE` | A SalesOrder is marked with status `CLOSED` while one or more associated Invoices remain unpaid or partially paid ($\text{outstanding\_balance} > 0$). | A SalesOrder status transition to `CLOSED` is forced in `sales_orders` and `status_events` despite unpaid invoices. |
| **ANOM-008** | `INVALID_STATUS_TRANSITION` | An entity bypasses mandatory lifecycle stages (e.g., Quote converts directly to Invoice; Order transitions from `DRAFT` directly to `FULFILLED`). | A `StatusEvent` records a direct transition violating the Allowed State Transition Matrix without requisite precursor states. |
| **ANOM-009** | `DISPUTE_AR_DISCONNECT` | A customer dispute is actively open/lodged, but the disputed amount is not isolated in A/R, remaining counted as normal collectible receivables. | An active dispute exists on an invoice, but financial reporting views treat the full gross balance as collectible without dispute flag. |
| **ANOM-010** | `SHORT_PAYMENT` | A customer remits a payment less than the invoice total, but no dispute or credit adjustment is lodged, leaving an unflagged residual balance. | A payment is allocated leaving an outstanding balance $< \$50.00$ that remains uncollected past payment terms with no dispute. |
| **ANOM-011** | `SLA_AGING_BREACH` | Operational processing delay exceeding acceptable enterprise business SLA thresholds. | Days elapsed between Order Confirmation and Shipment $> 3$ days, or Shipment Delivery to Invoice Issue $> 2$ days. |
| **ANOM-012** | `OVERDUE_UNPAID_INVOICE` | An invoice remains unpaid past its contractual net terms with no dispute lodged. | Invoice `issue_date` $+$ `payment_terms` $<$ Cutoff date, with $\text{outstanding\_balance} > 0.00$ and zero disputes. |

---

## 12. Detection & Evaluation Engine Requirements

### 12.1 Explainable Deterministic Detection Architecture
- **DET-001 (Deterministic Logic):** All anomaly detection routines must rely on deterministic SQL queries, set operations, or programmatic rule engines. No black-box machine learning models or probabilistic estimators shall be used for core exception detection.
- **DET-002 (Standardized Exception Output):** Each detected exception must produce an `ExceptionRecord` conforming to the schema defined in `DATA-015`.
- **DET-003 (Auditable Evidence & Record Traceability):** Every exception must include verifiable traceability to conflicting operational records. Evidence must link to the exact source row IDs (`source_table`, `source_id`, `conflicting_source_table`, `conflicting_source_id`) and capture expected vs. actual numerical values:
  - Source Order Line: `SO-2026-000104` / `OL-000412` (Ordered Qty: 10, Fulfilled Qty: 10)
  - Conflicting Invoice Line: `INV-2026-000120` / `IL-000588` (Invoiced Qty: 15)
  - Discrepancy Delta: $+5.00$ units (Overbilled by \$600.00)
- **DET-004 (Strict Ground-Truth Blindness):** The detection engine must execute exclusively against raw transactional and master tables. The ground-truth tables/files must never be mounted, imported, queried, or referenced by the detection logic.

### 12.2 Evaluation Metrics & Benchmarking
- **DET-005 (Evaluation Matrix):** An automated evaluation harness shall compare the set of detected exceptions $D$ against the set of ground-truth labeled exceptions $G$:
  - **True Positive (TP):** An anomaly in $G$ correctly identified in $D$ with matching `entity_id` and matching `issue_type`.
  - **False Positive (FP):** An anomaly identified in $D$ that does not exist in $G$ (a false alarm on legitimate business data).
  - **False Negative (FN):** An anomaly present in $G$ that was missed by $D$.
- **DET-006 (Statistical Metrics):** The evaluation harness must calculate:
  $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}, \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}, \quad \text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
- **DET-007 (Categorical Breakdown):** In addition to macro and micro global scores, evaluation reports must present precision, recall, and F1 broken down across each of the 10+ anomaly types.

---

## 13. Data Integrity & Validation Requirements

- **INT-001 (Primary Key Uniqueness):** 100% of rows across all tables must enforce unique primary keys without duplication or collisions.
- **INT-002 (Foreign Key Completeness):** Zero orphaned child records. All foreign keys must resolve to active, valid parent records.
- **INT-003 (Enum & Allowed Values):** All status fields, currency codes, payment methods, and dispute reasons must strictly adhere to documented enum definitions.
- **INT-004 (Monotonic Date Ordering):** Timestamps for dependent lifecycle stages must be sequentially valid ($\text{Quote} \le \text{Order} \le \text{Shipment} \le \text{Invoice} \le \text{Payment}$).
- **INT-005 (Line-to-Header Arithmetic Reconciliation):**
  - $\sum \text{QuoteLine.line\_net\_amount} = \text{Quote.total\_net\_amount}$
  - $\sum \text{OrderLine.line\_total\_amount} = \text{SalesOrder.total\_order\_value}$
  - $\sum \text{InvoiceLine.line\_total\_amount} = \text{Invoice.total\_invoiced\_amount}$
- **INT-006 (Payment Allocation Balancing):**
  - $\sum \text{PaymentAllocation.allocated\_amount} \le \text{Payment.amount\_received}$
  - $\sum \text{PaymentAllocation.allocated\_amount} \le \text{Invoice.total\_invoiced\_amount}$
- **INT-007 (Immutability of Audit History):** Once written, `StatusEvent` and `AuditLog` rows cannot be modified or deleted.

---

## 14. Expected System Outcomes

Upon full completion and deployment, the platform shall deliver:
- **OUT-001 (Direct PostgreSQL Inspection):** The entire relational database is directly inspectable via standard SQL queries, enabling evaluators to verify data hygiene, referential constraints, and event tables.
- **OUT-002 (360-Degree O2C Visual Lineage):** Visual and programmatic traceability of any commercial entity from Account creation through to Dispute settlement across independent lifecycles.
- **OUT-003 (Automated Revenue Leakage Dashboard):** Real-time aggregation of detected leakage, categorized by overbilling, underbilling, duplicate invoices, and payment over-allocations.
- **OUT-004 (Explainable Exception Dossiers):** Detailed drill-down views for finance and sales operations personnel providing exact evidence, source records, and recommended remediation for every exception.
- **OUT-005 (Audit & Compliance Verification):** Automated reporting on invalid lifecycle state transitions and skipped approvals.
- **OUT-006 (Benchmarking Report):** Automated generation of precision/recall evaluation matrices proving high accuracy against ground-truth benchmarks.

---

## 15. Acceptance Criteria

| Criteria ID | Domain | Detailed Acceptance Criteria | Verification Method |
| :--- | :--- | :--- | :--- |
| **AC-001** | Documentation | Complete, comprehensive `PROJECT_REQUIREMENTS.md` created in project-local `docs/` with all 16 sections, standard identifiers, and no code generation. | Document inspection |
| **AC-002** | Master Data | All master accounts enforce unique account numbers and valid credit limits. | SQL constraint check |
| **AC-003** | Identifiers | Business IDs strictly conform to regex formats: `QTE-2026-XXXXXX`, `SO-2026-XXXXXX`, `SHP-2026-XXXXXX`, `INV-2026-XXXXXX`, `PAY-2026-XXXXXX`, `DSP-2026-XXXXXX`. | Regex validation query |
| **AC-004** | Target Volume | Synthetic generator successfully produces 10,000 quotes, 7,000 orders, 8,000 invoices, and 15,000 discrete payments. | Row count queries |
| **AC-005** | Reproducibility | Two consecutive generator runs with seed `20261022` yield identical row counts and identical SHA-256 dataset checksums. | Automated diff/checksum test |
| **AC-006** | Ground Truth | Separate `ground_truth.csv`/`json` exported containing explicit `issue_type` and target entity IDs. | File inspection |
| **AC-007** | Detection Blindness | Detection engine executes and identifies exceptions without reading or accessing the ground-truth file. | Code and I/O audit |
| **AC-008** | Anomaly Coverage | All 10 mandated anomaly types are successfully synthesized, labeled, and detected by the engine. | Evaluation run output |
| **AC-009** | Evidence Traceability| 100% of generated `ExceptionRecord` entries link to traceable source record pointers with expected, actual, and delta values. | SQL query checking nulls |
| **AC-010** | Evaluation Metrics | Global Precision $\ge 0.95$, Recall $\ge 0.95$, and F1 Score $\ge 0.95$ achieved on the baseline synthetic benchmark. | Automated evaluation runner |
| **AC-011** | Audit Immutability | `StatusEvent` table preserves complete lifecycle state history with zero historical record overwrites. | Trigger / log audit |
| **AC-012** | Database Integrity | Zero foreign key violations, zero orphaned rows, and zero balance reconciliation errors on baseline valid records. | PostgreSQL integrity check script |

---

## 16. Comprehensive Unresolved Decision Register & Analysis

This register documents all eight (8) open business decisions in comprehensive detail. **In accordance with discovery governance, developer approval is required for all questions; no proposals are silently approved.**

---

### [OQ-001] Financial Rounding Tolerance
- **Description:** What is the acceptable numerical tolerance threshold for flagging underbilling or overbilling?
- **Business Impact:** Multi-line calculations involving fractional tax rates and percentage discounts often introduce cent-level rounding variances (\$0.01 to \$0.02). Setting an inappropriate threshold triggers high false positive rates, overburdening finance analysts with non-actionable alerts.
- **Proposed MVP Default:** **\$0.02 Tolerance Threshold**. Any mathematical variance $\le \$0.02$ between invoiced amount and expected contract amount is treated as a permissible rounding artifact; variances $> \$0.02$ are flagged as anomalies.
- **Alternative Approaches:**
  - *Alternative A (Strict Zero-Tolerance - \$0.00):* Flag every single discrepancy $> \$0.00$ without exception.
  - *Alternative B (Percentage-Based Threshold - e.g., 0.1% of line value):* Flag discrepancies exceeding a percentage threshold.
- **Consequences of Each Choice:**
  - *Strict Zero-Tolerance:* Guarantees 100% recall on synthetic data, but will yield numerous false positives on real-world multi-line invoices where rounding occurs across line taxes.
  - *Proposed \$0.02 Tolerance:* Eliminates rounding false positives while catching all genuine commercial pricing errors (\$1.00+), maximizing F1 score.
  - *Percentage Threshold:* Scales poorly on small items (e.g., \$10 item has \$0.01 threshold; \$50,000 item has \$50 threshold, potentially hiding real leakage).
- **Requires Developer Approval:** **YES**

---

### [OQ-002] Currency Scope & Multi-Currency Accounting
- **Description:** Does the platform operate exclusively in a single functional currency (`USD`), or must it support multi-currency transactions with historical FX conversions and realized gain/loss accounting?
- **Business Impact:** Multi-currency requirements fundamentally alter the database schema (adding FX rate tables, transaction vs. base currency fields, and date-effective exchange lookups) and payment allocation reconciliation rules.
- **Proposed MVP Default:** **Single Currency (`USD`)**. All accounts, quotes, orders, invoices, and payments operate strictly in USD.
- **Alternative Approaches:**
  - *Alternative A (Static Multi-Currency):* Allow currency codes (EUR, GBP, USD) on quotes/invoices, but require payments to match the invoice currency exactly (no FX conversion).
  - *Alternative B (Full FX Accounting Engine):* Ingest daily FX rate tables, convert foreign currency invoices to base currency at issue date, and record realized FX gains/losses upon payment settlement.
- **Consequences of Each Choice:**
  - *Proposed Single Currency:* Keeps the hackathon MVP highly focused on core revenue leakage logic and deterministic reconciliation, meeting all core prompt requirements without bloat.
  - *Alternative A:* Adds minor enum validation complexity without solving cross-currency cash matching.
  - *Alternative B:* Drastically increases implementation overhead and risk of false-positive leakage flags due to exchange rate timing variances.
- **Requires Developer Approval:** **YES**

---

### [OQ-003] SLA Aging Cutoffs and Processing Timelines
- **Description:** What are the exact business SLA duration thresholds for identifying processing delays and overdue transactions (`ANOM-011` / `ANOM-012`)?
- **Business Impact:** Setting SLAs too aggressively flags normal operational buffers as anomalies; setting them too loosely misses genuine operational bottlenecks and aging risks.
- **Proposed MVP Default:**
  - Order Confirmation to Shipment Dispatch: **3 calendar days** (Breach $> 3$ days)
  - Shipment Delivery to Invoice Generation: **2 calendar days** (Breach $> 2$ days)
  - Invoice Issue to Payment Due Date: **Governed by Account Payment Terms** (`NET30` = 30 days, `NET60` = 60 days)
  - Dispute Lodged to Resolution: **14 calendar days** (Breach $> 14$ days)
- **Alternative Approaches:**
  - *Alternative A (Strict 24-48 Hour SLAs):* All transitions must occur within 24 to 48 hours.
  - *Alternative B (Configurable Business Days with Holiday Calendars):* Exclude weekends and corporate holidays using a dynamic calendar table.
- **Consequences of Each Choice:**
  - *Proposed Default:* Clear, deterministic, easily calculable using standard SQL timestamp arithmetic (`NOW() - dispatched_at > INTERVAL '2 days'`).
  - *Alternative A:* Unrealistic for enterprise physical logistics and will create false positives on standard weekend cycles.
  - *Alternative B:* Increases architectural complexity; unnecessary for a synthetic dataset evaluation environment unless explicitly required.
- **Requires Developer Approval:** **YES**

---

### [OQ-004] Dispute Accounts-Receivable Isolation Policy
- **Description:** When an active dispute is lodged against an invoice, how should the Accounts Receivable (A/R) balance be reflected in financial reporting?
- **Business Impact:** Directly dictates how the A/R reconciliation engine and `ANOM-009` (`DISPUTE_AR_DISCONNECT`) are validated. Failing to isolate disputed balances leads to unlawful collections actions and distorted financial audits.
- **Proposed MVP Default:** **Line-Level / Disputed Amount Segregation**. Only the specific `disputed_amount` is isolated into a separate `disputed_ar_balance` bucket; the undisputed remainder of the invoice remains in active collectible A/R.
- **Alternative Approaches:**
  - *Alternative A (Full Invoice Freeze):* The entire gross invoice balance is frozen and marked `DISPUTED`, halting all collections for that invoice.
  - *Alternative B (No A/R Modification):* The dispute is tracked purely as a customer support ticket without altering A/R reporting (this constitutes the actual anomaly we must detect!).
- **Consequences of Each Choice:**
  - *Proposed Default:* Aligns with standard enterprise accounting practices (e.g. Oracle/SAP A/R), preventing revenue leakage while preserving legitimate cash collections on undisputed portions.
  - *Alternative A:* Simpler to implement at the invoice header level, but financially inaccurate if a customer disputes a \$50 damaged item on a \$100,000 equipment invoice.
  - *Alternative B:* Violates GAAP revenue recognition and causes severe A/R distortion.
- **Requires Developer Approval:** **YES**

---

### [OQ-005] Partial Shipment Invoicing Consolidation Policy
- **Description:** Can multiple partial shipments across different dates be consolidated into a single invoice, or must every shipment event trigger its own discrete invoice?
- **Business Impact:** Governs the relational cardinality between `Shipment`, `ShipmentLine`, `Invoice`, and `InvoiceLine`, and determines how the billing reconciliation engine checks unbilled fulfillments.
- **Proposed MVP Default:** **Shipment-Based Invoicing (1:1 Shipment to Invoice)**. Each distinct shipment dispatch triggers a corresponding invoice for the specific items and quantities delivered in that shipment.
- **Alternative Approaches:**
  - *Alternative A (Consolidated Monthly/Milestone Invoicing):* Multiple shipments within a billing cycle are grouped into a single consolidated invoice per Sales Order.
  - *Alternative B (Hybrid Invoicing):* Support both shipment-based and consolidated order-based invoicing based on an Account-level billing preference flag.
- **Consequences of Each Choice:**
  - *Proposed Default:* Clean, 1:1 traceability between `shipment_id` and `invoice_id`, simplifying duplicate billing detection and quantity reconciliation.
  - *Alternative A:* Requires complex date-window grouping logic and increases the difficulty of isolating which specific shipment line was overbilled or underbilled.
  - *Alternative B:* Adds unnecessary configuration branching for MVP discovery.
- **Requires Developer Approval:** **YES**

---

### [OQ-006] Cash Overpayment & Unallocated Balance Policy
- **Description:** If a customer remits a payment exceeding the total open balance of their invoices ($\text{amount\_received} > \sum \text{outstanding\_balance}$), how should the surplus cash be treated?
- **Business Impact:** Dictates whether unallocated funds are treated as legitimate customer credit balances or flagged as operational anomalies / money laundering risks.
- **Proposed MVP Default:** **Customer Credit Balance with Audit Alert**. The surplus amount remains in `payments.unallocated_amount` as a customer credit on the Account, but an informational alert is logged if unallocated funds remain unapplied past 30 days.
- **Alternative Approaches:**
  - *Alternative A (Strict Anomaly Flagging):* Any payment exceeding open invoice balances is immediately flagged as an `EXCESSIVE_PAYMENT_RECEIVED` exception.
  - *Alternative B (Automatic Return/Refund):* Automatically generate a `REFUNDED` payment event for the surplus amount.
- **Consequences of Each Choice:**
  - *Proposed Default:* Realistic enterprise treasury behavior; customers frequently pay round sums or prepay for future orders.
  - *Alternative A:* May produce false alarms if customer prepayments are legally permitted.
  - *Alternative B:* Complex banking reversal workflow outside the scope of hackathon MVP.
- **Requires Developer Approval:** **YES**

---

### [OQ-007] Sales Order Closure Definition
- **Description:** What exact operational and financial conditions are required for a Sales Order to transition to `CLOSED`?
- **Business Impact:** Directly defines the detection rule for `ANOM-007` (`PREMATURE_ORDER_CLOSURE`). If an order can close operationally while invoices are open, the detection rule must evaluate A/R separately from WMS fulfillment.
- **Proposed MVP Default:** **Strict Integrated Closure (Physical & Financial)**. A SalesOrder can ONLY transition to `CLOSED` when:
  1. 100% of order line quantities have been fulfilled (or explicitly cancelled/short-closed); AND
  2. All associated invoices have `status = 'PAID'` with `outstanding_balance = 0.00`; AND
  3. Zero open disputes exist.  
  *Any order marked `CLOSED` with unpaid invoices is flagged as `PREMATURE_ORDER_CLOSURE`.*
- **Alternative Approaches:**
  - *Alternative A (Operational Closure Only):* An order transitions to `CLOSED` purely when logistics fulfillment is 100% delivered; financial settlement is tracked purely at the invoice/account level.
  - *Alternative B (Two Separate Closure Fields):* Maintain `fulfillment_status = 'CLOSED'` and `financial_status = 'SETTLED'`.
- **Consequences of Each Choice:**
  - *Proposed Default:* Directly fulfills the explicit prompt requirement: *"Order is closed while an invoice remains unpaid"*. Simple, unambiguous rule for anomaly detection.
  - *Alternative A:* Contradicts the prompt's explicit anomaly definition #4.
  - *Alternative B:* Adds schema complexity; would require altering the core entity definition.
- **Requires Developer Approval:** **YES**

---

### [OQ-008] Discount and Tax Calculation Level
- **Description:** Are discounts and taxes applied strictly at the line-item level, or can global discounts/taxes be applied at the Quote/Order/Invoice header?
- **Business Impact:** Governs line-to-header arithmetic integrity (`INT-005`) and determines whether prorated rounding anomalies can occur across lines.
- **Proposed MVP Default:** **Line-Level Calculation Only**. Discounts are applied directly to each `QuoteLine` and `OrderLine`. Header totals are strictly derived by summing line-level totals. No arbitrary header-level manual overrides are permitted.
- **Alternative Approaches:**
  - *Alternative A (Header-Level Discounts with Pro-Rata Allocation):* Allow header-level discounts (e.g., \$500 off order) that are prorated across lines based on line value.
  - *Alternative B (Compound Discounts):* Support both line-item trade discounts and header-level cash settlement discounts.
- **Consequences of Each Choice:**
  - *Proposed Default:* Guarantees exact mathematical reconciliation: $\sum \text{line\_net\_amount} = \text{header\_total}$ with zero proration rounding errors. Perfect for deterministic revenue leakage detection.
  - *Alternative A & B:* Introduces fractional rounding remainders across odd numbers of items, creating potential false positives in underbilling detectors.
- **Requires Developer Approval:** **YES**

---

### [OQ-009] Volume Register Confirmation for Payments vs. Allocations
- **Description:** Does the required target volume of **15,000** apply strictly to discrete `Payment` records, or to the total count of `PaymentAllocation` records?
- **Business Impact:** Affects synthetic generator sizing, database indexing, and memory allocation during evaluation.
- **Proposed MVP Default:** **15,000 Discrete Payment Records**, which dynamically generate approximately 18,000 to 22,000 `PaymentAllocation` bridge records based on realistic enterprise split-remittance modeling.
- **Alternative Approaches:**
  - *Alternative A (Allocation Capped):* Target 15,000 `PaymentAllocation` records generated from approximately 10,000 discrete payments.
- **Requires Developer Approval:** **YES**

---

*End of Project Requirements Specification v1.1.0.*  
*Awaiting Developer / Stakeholder Approval before progressing to Architecture & Implementation.*
