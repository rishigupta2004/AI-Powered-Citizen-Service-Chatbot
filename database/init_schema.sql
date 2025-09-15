CREATE TABLE IF NOT EXISTS services (
    service_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    category VARCHAR(80),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS procedures (
    procedure_id SERIAL PRIMARY KEY,
    service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
    title TEXT,
    steps TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    doc_id SERIAL PRIMARY KEY,
    service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
    name VARCHAR(150),
    description TEXT,
    mandatory BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS faqs (
    faq_id SERIAL PRIMARY KEY,
    service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
    question TEXT,
    answer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(150),
    email VARCHAR(200) UNIQUE,
    role VARCHAR(50) DEFAULT 'citizen',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
