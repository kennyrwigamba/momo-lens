-- MoMo Lens - CRUD Operations & Verification

USE momo_lens_db;

-- CREATE: Insert test user, transaction and category map
INSERT INTO users (phone_number, full_name, user_type) 
VALUES ('250788777777', 'Kigali Supermarket', 'MERCHANT');

INSERT INTO transactions 
(transaction_id, sender_id, receiver_id, amount, currency, fee, balance_after, tx_timestamp, status, raw_sms_body)
VALUES 
('TX_NEW_01', 1, LAST_INSERT_ID(), 12000.00, 'RWF', 0.00, 10000.00, NOW(), 'COMPLETED', 'Payment of 12000 RWF to Kigali Supermarket.');

INSERT INTO transaction_category_map (transaction_id, category_id, is_primary) 
VALUES ('TX_NEW_01', 2, 1);

-- READ: Get transactions with sender, receiver and primary category
SELECT 
    t.transaction_id,
    s.full_name AS sender,
    r.full_name AS receiver,
    t.amount,
    t.currency,
    t.fee,
    t.balance_after,
    c.category_name AS category,
    t.tx_timestamp
FROM transactions t
JOIN users s ON t.sender_id = s.user_id
JOIN users r ON t.receiver_id = r.user_id
JOIN transaction_category_map m ON t.transaction_id = m.transaction_id AND m.is_primary = 1
JOIN transaction_categories c ON m.category_id = c.category_id
ORDER BY t.tx_timestamp DESC;

-- READ: Demonstrate Many-to-Many categories per transaction
SELECT 
    t.transaction_id,
    t.amount,
    t.currency,
    GROUP_CONCAT(c.category_name SEPARATOR ', ') AS categories
FROM transactions t
JOIN transaction_category_map m ON t.transaction_id = m.transaction_id
JOIN transaction_categories c ON m.category_id = c.category_id
GROUP BY t.transaction_id, t.amount, t.currency;

-- READ: Daily category summary aggregation
SELECT 
    DATE(t.tx_timestamp) AS tx_date,
    c.category_name,
    COUNT(t.transaction_id) AS total_count,
    SUM(t.amount) AS total_volume_rwf,
    SUM(t.fee) AS total_fees_rwf
FROM transactions t
JOIN transaction_category_map m ON t.transaction_id = m.transaction_id AND m.is_primary = 1
JOIN transaction_categories c ON m.category_id = c.category_id
GROUP BY DATE(t.tx_timestamp), c.category_name;

-- UPDATE: Update transaction status
UPDATE transactions 
SET status = 'REVERSED' 
WHERE transaction_id = 'TX_NEW_01';

-- DELETE: Delete test transaction (cascades to junction table)
DELETE FROM transactions 
WHERE transaction_id = 'TX_NEW_01';
