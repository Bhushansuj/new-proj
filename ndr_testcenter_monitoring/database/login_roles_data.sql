USE bhushan;

INSERT IGNORE INTO roles (id, role_name) VALUES
(1, 'admin'),
(2, 'mitarbeiter');

INSERT INTO users (id, username, password_hash, role_id)
VALUES
(1, 'admin', 'admin123', 1),
(2, 'mitarbeiter', 'mitarbeiter123', 2)
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
    password_hash = VALUES(password_hash),
    role_id = VALUES(role_id);
