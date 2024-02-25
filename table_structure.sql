
-- Plans table
CREATE TABLE plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    features TEXT
);



-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    2fa VARCHAR(255),
    plan_id INT,
    status VARCHAR(20),
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);




-- Registrars table
CREATE TABLE registrars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255),
    api_token VARCHAR(255),
    user_id INT,
    note TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


-- Domains table
CREATE TABLE domains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    registrar_id INT,
    user_id INT,
    status VARCHAR(20),
    ssl_status VARCHAR(20),
    http_response INT,
    note TEXT,
    FOREIGN KEY (registrar_id) REFERENCES registrars(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
