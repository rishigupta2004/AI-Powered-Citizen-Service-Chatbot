-- init_schema.sql (put this in gov-chatbot/database/)
CREATE EXTENSION IF NOT EXISTS IF NOT EXISTS pg_trgm;  -- optional helper for text search

-- Services
CREATE TABLE IF NOT EXISTS services (
  service_id SERIAL PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  slug VARCHAR(150) UNIQUE,
  description TEXT,
  category VARCHAR(80),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Procedures (steps / how-to)
CREATE TABLE IF NOT EXISTS procedures (
  procedure_id SERIAL PRIMARY KEY,
  service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
  title TEXT,
  steps TEXT,   -- can store JSON or plain text for step-by-step
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Documents required for services
CREATE TABLE IF NOT EXISTS documents (
  doc_id SERIAL PRIMARY KEY,
  service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
  name VARCHAR(150),
  description TEXT,
  mandatory BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- FAQs per service
CREATE TABLE IF NOT EXISTS faqs (
  faq_id SERIAL PRIMARY KEY,
  service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
  question TEXT,
  answer TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Basic users table for admin/testing
CREATE TABLE IF NOT EXISTS users (
  user_id SERIAL PRIMARY KEY,
  name VARCHAR(150),
  email VARCHAR(200) UNIQUE,
  role VARCHAR(50) DEFAULT 'editor',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
