CREATE DATABASE IF NOT EXISTS trabalho_finance
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE trabalho_finance;

CREATE TABLE transaction (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    client VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment VARCHAR(50),
    notes TEXT,
    created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
