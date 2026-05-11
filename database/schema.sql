CREATE DATABASE IF NOT EXISTS ndr_testcenter;
USE ndr_testcenter;

CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL UNIQUE,
    mac_address VARCHAR(17),
    model VARCHAR(100),
    location VARCHAR(100),
    os_build VARCHAR(50),
    status VARCHAR(20) DEFAULT 'unknown',
    is_virtual BOOLEAN DEFAULT FALSE,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE users (
    username VARCHAR(100) PRIMARY KEY,
    password VARCHAR(255)
);
