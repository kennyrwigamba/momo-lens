-- MoMo Lens Database Setup

CREATE DATABASE IF NOT EXISTS momo_lens_db;
USE momo_lens_db;

-- Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique ID for the user',
    phone_number VARCHAR(20) NOT NULL UNIQUE COMMENT 'Unique phone number for the user',
    full_name VARCHAR(100) NOT NULL COMMENT 'Full registered name of the customer/business',
    user_type ENUM('INDIVIDUAL', 'MERCHANT', 'AGENT', 'BANK', 'SYSTEM') NOT NULL DEFAULT 'INDIVIDUAL' COMMENT 'Role classification in the MoMo ecosystem',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when user was created'
);

-- Transaction Categories Table
CREATE TABLE transaction_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique ID for the transaction category',
    category_code VARCHAR(30) NOT NULL UNIQUE COMMENT 'Short code: P2P_TRANSFER, MERCHANT_PAYMENT, etc.',
    category_name VARCHAR(100) NOT NULL COMMENT 'Descriptive title of the category',
    description VARCHAR(255) NULL COMMENT 'Explanation of transaction classification rules',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when category was added'
);

-- Transactions Ledger Table
CREATE TABLE transactions (
    transaction_id VARCHAR(64) PRIMARY KEY COMMENT 'Official telecom financial transaction ID (e.g. TxId)',
    sender_id INT NOT NULL COMMENT 'FK to users table (payer/debit account)',
    receiver_id INT NOT NULL COMMENT 'FK to users table (payee/credit account)',
    amount DECIMAL(12, 2) NOT NULL COMMENT 'Monetary value transferred',
    currency VARCHAR(3) NOT NULL DEFAULT 'RWF' COMMENT 'Three-letter currency code',
    fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Network transaction charge applied',
    balance_after DECIMAL(12, 2) NOT NULL COMMENT 'Account balance after transaction execution',
    tx_timestamp DATETIME NOT NULL COMMENT 'Carrier timestamp when transaction completed',
    status ENUM('COMPLETED', 'PENDING', 'FAILED', 'REVERSED') NOT NULL DEFAULT 'COMPLETED' COMMENT 'Transaction state',
    raw_sms_body TEXT NULL COMMENT 'Original carrier SMS string for auditability',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record insertion timestamp',

    -- Foreign Keys
    CONSTRAINT fk_tx_sender FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_tx_receiver FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Accuracy & Security Constraints
    CONSTRAINT chk_amount_pos CHECK (amount > 0),
    CONSTRAINT chk_fee_non_neg CHECK (fee >= 0),
    CONSTRAINT chk_balance_non_neg CHECK (balance_after >= 0)
);

-- Junction Table (M:N Resolution)
CREATE TABLE transaction_category_map (
    map_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique ID for the mapping',
    transaction_id VARCHAR(64) NOT NULL COMMENT 'FK to transactions table',
    category_id INT NOT NULL COMMENT 'FK to transaction_categories table',
    is_primary TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1 = primary category, 0 = secondary tag',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Mapping timestamp',

    CONSTRAINT fk_map_tx FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_map_cat FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_tx_cat UNIQUE (transaction_id, category_id)
);

-- System Logs Table
CREATE TABLE system_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique log ID',
    process_name VARCHAR(50) NOT NULL COMMENT 'Service or script name (e.g. XML_PARSER, DB_LOADER)',
    status ENUM('SUCCESS', 'WARNING', 'ERROR') NOT NULL COMMENT 'Job execution outcome',
    records_processed INT NOT NULL DEFAULT 0 COMMENT 'Count of processed records',
    message TEXT NULL COMMENT 'Descriptive execution logs or error traces',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Log event timestamp'
);

-- Performance Indexes
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_tx_timestamp ON transactions(tx_timestamp);
CREATE INDEX idx_cat_code ON transaction_categories(category_code);

-- Sample Data

-- Seed Users
INSERT INTO users (user_id, phone_number, full_name, user_type) VALUES
(1, '250788110381', 'Account Owner', 'INDIVIDUAL'),
(2, '250791666666', 'Jane Uwera', 'INDIVIDUAL'),
(3, '250790777777', 'Sam Kalisa', 'INDIVIDUAL'),
(4, '250788999999', 'Linda Muhoza', 'INDIVIDUAL'),
(5, '250795963036', 'PayPal PAYMENT LTD', 'MERCHANT');

-- Seed Categories
INSERT INTO transaction_categories (category_id, category_code, category_name, description) VALUES
(1, 'P2P_TRANSFER', 'Peer-to-Peer Transfer', 'Transfer between individual mobile money subscribers'),
(2, 'MERCHANT_PAYMENT', 'Merchant Payment', 'Payments made to merchant codes'),
(3, 'BANK_DEPOSIT', 'Bank Deposit', 'Funds deposited from bank to mobile wallet'),
(4, 'AIRTIME_PURCHASE', 'Airtime Purchase', 'Top-up of airtime or data bundles'),
(5, 'UTILITY_BILL', 'Utility Bill', 'Payments for water, power, or utilities');

-- Seed Transactions
INSERT INTO transactions (transaction_id, sender_id, receiver_id, amount, currency, fee, balance_after, tx_timestamp, status, raw_sms_body) VALUES
('76662021700', 2, 1, 20000.00, 'RWF', 0.00, 70000.00, '2026-09-10 09:15:00', 'COMPLETED', 
 'You have received 20,000 RWF from Jane Uwera (250791666666). New balance: 70,000 RWF. Financial Transaction Id: 76662021700.'),

('51732411227', 1, 3, 600.00, 'RWF', 20.00, 69380.00, '2026-09-11 11:30:00', 'COMPLETED', 
 'TxId: 51732411227. 600 RWF transferred to Sam Kalisa (250790777777). Fee: 20 RWF. New balance: 69,380 RWF.'),

('73214484437', 1, 2, 1000.00, 'RWF', 100.00, 68280.00, '2026-09-12 14:20:00', 'COMPLETED', 
 'TxId: 73214484437. 1,000 RWF transferred to Jane Uwera (250791666666). Fee: 100 RWF. New balance: 68,280 RWF.'),

('17818959211', 1, 3, 2000.00, 'RWF', 100.00, 66180.00, '2026-09-13 16:45:00', 'COMPLETED', 
 'TxId: 17818959211. 2,000 RWF transferred to Sam Kalisa (250790777777). Fee: 100 RWF. New balance: 66,180 RWF.'),

('13947831685', 1, 5, 25000.00, 'RWF', 250.00, 40930.00, '2026-09-14 10:10:00', 'COMPLETED', 
 'TxId: 13947831685. Payment of 25,000 RWF to PayPal PAYMENT LTD completed. Fee: 250 RWF. New balance: 40,930 RWF.');

-- Seed Category Mappings
INSERT INTO transaction_category_map (transaction_id, category_id, is_primary) VALUES
('76662021700', 1, 1),
('73214484437', 2, 1),
('51732411227', 2, 1),
('17818959211', 2, 1),
('13947831685', 2, 1),
('13947831685', 5, 0);

-- Seed System Logs
INSERT INTO system_logs (process_name, status, records_processed, message) VALUES
('XML_PARSER', 'SUCCESS', 1691, 'Parsed input XML dataset'),
('NORMALIZER', 'SUCCESS', 1691, 'Cleaned phone numbers and normalized amounts'),
('DB_LOADER', 'SUCCESS', 5, 'Sample batch inserted successfully'),
('SECURITY_CHECK', 'SUCCESS', 5, 'Verified check constraints and balance invariants'),
('AGGREGATOR', 'SUCCESS', 5, 'Generated daily transaction summary view');
