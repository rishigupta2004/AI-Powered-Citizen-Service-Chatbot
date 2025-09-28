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

    -- Ingestion metadata
    source VARCHAR(100),
    file_name TEXT,
    language VARCHAR(10) DEFAULT 'en',
    doc_type VARCHAR(50) DEFAULT 'pdf',

    -- Business metadata
    name VARCHAR(150),
    description TEXT,
    mandatory BOOLEAN DEFAULT TRUE,

    -- System fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
