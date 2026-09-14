-- MoMo Lens Database Setup

CREATE DATABASE momo_lens_db;
USE momo_lens_db;

-- Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    user_type ENUM('INDIVIDUAL', 'MERCHANT', 'AGENT', 'BANK', 'SYSTEM') NOT NULL DEFAULT 'INDIVIDUAL',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Categories Table
CREATE TABLE transaction_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_code VARCHAR(30) NOT NULL UNIQUE,
    category_name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Transactions Ledger Table
CREATE TABLE transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'RWF',
    fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    balance_after DECIMAL(12, 2) NOT NULL,
    tx_timestamp DATETIME NOT NULL,
    status ENUM('COMPLETED', 'PENDING', 'FAILED', 'REVERSED') NOT NULL DEFAULT 'COMPLETED',
    raw_sms_body TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

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
    map_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(64) NOT NULL,
    category_id INT NOT NULL,
    is_primary TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_map_tx FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_map_cat FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_tx_cat UNIQUE (transaction_id, category_id)
);

-- System Logs Table
CREATE TABLE system_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    process_name VARCHAR(50) NOT NULL,
    status ENUM('SUCCESS', 'WARNING', 'ERROR') NOT NULL,
    records_processed INT NOT NULL DEFAULT 0,
    message TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_tx_timestamp ON transactions(tx_timestamp);
CREATE INDEX idx_cat_code ON transaction_categories(category_code);