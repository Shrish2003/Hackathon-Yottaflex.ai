-- ============================================================================
-- O2C REVENUE ASSURANCE PLATFORM: READ-ONLY DATABASE DIAGNOSTICS
-- Database: o2c_revenue_db
-- Engine: PostgreSQL 15+
-- Purpose: Audit record counts, integrity metrics, and leakage detection status
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. GLOBAL TABLE RECORD COUNTS (READ-ONLY)
-- ----------------------------------------------------------------------------
SELECT 'accounts' AS table_name, count(*) AS total_records FROM accounts
UNION ALL
SELECT 'quotes', count(*) FROM quotes
UNION ALL
SELECT 'quote_lines', count(*) FROM quote_lines
UNION ALL
SELECT 'sales_orders', count(*) FROM sales_orders
UNION ALL
SELECT 'order_lines', count(*) FROM order_lines
UNION ALL
SELECT 'shipments', count(*) FROM shipments
UNION ALL
SELECT 'shipment_lines', count(*) FROM shipment_lines
UNION ALL
SELECT 'invoices', count(*) FROM invoices
UNION ALL
SELECT 'invoice_lines', count(*) FROM invoice_lines
UNION ALL
SELECT 'payments', count(*) FROM payments
UNION ALL
SELECT 'payment_allocations', count(*) FROM payment_allocations
UNION ALL
SELECT 'disputes', count(*) FROM disputes
UNION ALL
SELECT 'status_events', count(*) FROM status_events
UNION ALL
SELECT 'exception_records', count(*) FROM exception_records
UNION ALL
SELECT 'exception_evidence', count(*) FROM exception_evidence
UNION ALL
SELECT 'alembic_version', count(*) FROM alembic_version;


-- ----------------------------------------------------------------------------
-- 2. SALES ORDERS FINANCIAL SUMMARY
-- ----------------------------------------------------------------------------
SELECT 
    status,
    count(*) AS order_count,
    coalesce(sum(total_order_value), 0.0) AS total_value_inr,
    coalesce(min(total_order_value), 0.0) AS min_order_value,
    coalesce(max(total_order_value), 0.0) AS max_order_value,
    coalesce(avg(total_order_value), 0.0) AS avg_order_value
FROM sales_orders
GROUP BY status
ORDER BY order_count DESC;


-- ----------------------------------------------------------------------------
-- 3. INVOICES & OUTSTANDING RECEIVABLES SUMMARY
-- ----------------------------------------------------------------------------
SELECT 
    status,
    count(*) AS invoice_count,
    coalesce(sum(total_invoiced_amount), 0.0) AS total_invoiced_inr,
    coalesce(sum(paid_amount), 0.0) AS total_paid_inr,
    coalesce(sum(outstanding_balance), 0.0) AS total_outstanding_inr
FROM invoices
GROUP BY status
ORDER BY invoice_count DESC;


-- ----------------------------------------------------------------------------
-- 4. TREASURY PAYMENTS & UNALLOCATED CASH SUMMARY
-- ----------------------------------------------------------------------------
SELECT 
    payment_method,
    status,
    count(*) AS payment_count,
    coalesce(sum(amount_received), 0.0) AS total_received_inr,
    coalesce(sum(amount_allocated), 0.0) AS total_allocated_inr,
    coalesce(sum(unallocated_amount), 0.0) AS total_unallocated_inr
FROM payments
GROUP BY payment_method, status
ORDER BY total_received_inr DESC;


-- ----------------------------------------------------------------------------
-- 5. REVENUE LEAKAGE DETECTION EXCEPTIONS BY SEVERITY
-- ----------------------------------------------------------------------------
SELECT 
    severity,
    count(*) AS exception_count,
    coalesce(sum(leakage_amount), 0.0) AS quantified_leakage_inr
FROM exception_records
GROUP BY severity
ORDER BY 
    CASE severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
        ELSE 5
    END;


-- ----------------------------------------------------------------------------
-- 6. REVENUE LEAKAGE DETECTION EXCEPTIONS BY ANOMALY RULE
-- ----------------------------------------------------------------------------
SELECT 
    issue_type AS anomaly_rule,
    count(*) AS exception_count,
    coalesce(sum(leakage_amount), 0.0) AS total_leakage_inr
FROM exception_records
GROUP BY issue_type
ORDER BY exception_count DESC;


-- ----------------------------------------------------------------------------
-- 7. INTERNAL EVALUATION GROUND-TRUTH RECORD COUNTS
-- WARNING: Ground truth is strictly for offline engineering verification.
-- NEVER query, import, or expose this table in application APIs or UI.
-- ----------------------------------------------------------------------------
SELECT 
    issue_type AS ground_truth_anomaly,
    count(*) AS ground_truth_count,
    coalesce(sum(leakage_amount), 0.0) AS ground_truth_leakage_inr
FROM ground_truth_anomalies
GROUP BY issue_type
ORDER BY ground_truth_count DESC;
