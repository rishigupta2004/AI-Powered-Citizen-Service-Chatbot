-- =====================================================
-- GOVERNMENT SERVICES DATA WAREHOUSE SCHEMA
-- Enhanced schema for comprehensive citizen services database
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- CORE ENTITIES
-- =====================================================

-- Government Services (Enhanced)
CREATE TABLE IF NOT EXISTS services (
    service_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    
    -- Basic Information
    name VARCHAR(200) NOT NULL,
    short_name VARCHAR(50),
    description TEXT,
    category VARCHAR(100) NOT NULL, -- passport, aadhaar, pan, etc.
    subcategory VARCHAR(100),
    
    -- Government Metadata
    ministry VARCHAR(150),
    department VARCHAR(150),
    authority VARCHAR(150),
    official_website VARCHAR(500),
    
    -- Service Status
    is_active BOOLEAN DEFAULT TRUE,
    is_online_available BOOLEAN DEFAULT FALSE,
    is_api_available BOOLEAN DEFAULT FALSE,
    
    -- Multilingual Support
    languages_supported TEXT[], -- ['en', 'hi', 'bn', 'ta', 'te', 'mr', 'gu']
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Service Procedures (Enhanced)
CREATE TABLE IF NOT EXISTS procedures (
    procedure_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    service_id INTEGER REFERENCES services(service_id) ON DELETE CASCADE,
    
    -- Procedure Information
    title VARCHAR(300) NOT NULL,
    short_title VARCHAR(150),
    description TEXT,
    procedure_type VARCHAR(50), -- application, renewal, correction, etc.
    
    -- Steps and Instructions
    steps JSONB, -- Structured steps with metadata
    prerequisites TEXT[],
    estimated_time VARCHAR(50), -- "15 minutes", "1 hour", etc.
    difficulty_level VARCHAR(20), -- easy, medium, hard
    
    -- Fees and Costs
    fee_structure JSONB, -- Different fee tiers
    is_free BOOLEAN DEFAULT FALSE,
    
    -- Processing Information
    processing_time VARCHAR(100), -- "7-10 working days"
    tatkal_available BOOLEAN DEFAULT FALSE,
    tatkal_fee DECIMAL(10,2),
    
    -- Multilingual Support
    language VARCHAR(10) DEFAULT 'en',
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Document Requirements (Enhanced)
CREATE TABLE IF NOT EXISTS documents (
    doc_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    service_id INTEGER REFERENCES services(service_id) ON DELETE CASCADE,
    procedure_id INTEGER REFERENCES procedures(procedure_id) ON DELETE CASCADE,
    
    -- Document Information
    name VARCHAR(300) NOT NULL,
    short_name VARCHAR(100),
    description TEXT,
    document_type VARCHAR(50), -- identity, address, income, etc.
    
    -- Requirements
    is_mandatory BOOLEAN DEFAULT TRUE,
    is_original_required BOOLEAN DEFAULT TRUE,
    copies_required INTEGER DEFAULT 1,
    validity_period VARCHAR(100), -- "6 months", "1 year", etc.
    
    -- File Information
    file_format VARCHAR(20) DEFAULT 'pdf', -- pdf, jpg, png, etc.
    max_file_size_mb INTEGER DEFAULT 5,
    accepted_formats TEXT[], -- ['pdf', 'jpg', 'png']
    
    -- Source Information
    source VARCHAR(100), -- apisetu, scraping, manual
    source_url VARCHAR(500),
    file_name VARCHAR(300),
    
    -- Processing Information
    language VARCHAR(10) DEFAULT 'en',
    is_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    
    -- Content Storage
    raw_content TEXT, -- Extracted text content
    structured_content JSONB, -- Parsed structured data
    metadata JSONB, -- Additional metadata
    
    -- Vector Embeddings
    embedding VECTOR(384), -- For semantic search
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- FAQs (Enhanced)
CREATE TABLE IF NOT EXISTS faqs (
    faq_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    service_id INTEGER REFERENCES services(service_id) ON DELETE CASCADE,
    procedure_id INTEGER REFERENCES procedures(procedure_id) ON DELETE CASCADE,
    
    -- FAQ Content
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    short_answer TEXT, -- Brief version
    
    -- Categorization
    category VARCHAR(100), -- general, technical, troubleshooting
    tags TEXT[], -- ['fees', 'documents', 'timeline']
    
    -- Multilingual Support
    language VARCHAR(10) DEFAULT 'en',
    
    -- Vector Embeddings
    question_embedding VECTOR(384),
    answer_embedding VECTOR(384),
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- DATA INGESTION & PROCESSING
-- =====================================================

-- Raw Scraped Content
CREATE TABLE IF NOT EXISTS raw_content (
    content_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    
    -- Source Information
    source_type VARCHAR(50) NOT NULL, -- api, scraping, pdf, ocr
    source_url VARCHAR(500),
    source_name VARCHAR(200),
    
    -- Content Information
    title VARCHAR(500),
    content TEXT NOT NULL,
    content_type VARCHAR(50), -- html, pdf, text, json
    language VARCHAR(10) DEFAULT 'en',
    
    -- Processing Information
    is_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    processing_errors TEXT,
    
    -- Metadata
    metadata JSONB,
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Content Chunks (for vector search)
CREATE TABLE IF NOT EXISTS content_chunks (
    chunk_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    content_id INTEGER REFERENCES raw_content(content_id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(service_id) ON DELETE CASCADE,
    
    -- Chunk Information
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_type VARCHAR(50), -- paragraph, section, step, etc.
    
    -- Vector Embeddings
    embedding VECTOR(384),
    
    -- Metadata
    metadata JSONB,
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- OFFICES & LOCATIONS
-- =====================================================

-- Government Offices
CREATE TABLE IF NOT EXISTS offices (
    office_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    service_id INTEGER REFERENCES services(service_id) ON DELETE CASCADE,
    
    -- Office Information
    name VARCHAR(300) NOT NULL,
    office_type VARCHAR(100), -- PSK, RTO, Passport Office, etc.
    
    -- Location Information
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    district VARCHAR(100),
    
    -- Contact Information
    phone VARCHAR(20)[],
    email VARCHAR(200)[],
    website VARCHAR(500),
    
    -- Operating Hours
    operating_hours JSONB, -- Structured hours data
    is_24x7 BOOLEAN DEFAULT FALSE,
    
    -- Services Offered
    services_offered TEXT[],
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- FEES & COSTS
-- =====================================================

-- Fee Structure
CREATE TABLE IF NOT EXISTS fees (
    fee_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    service_id INTEGER REFERENCES services(service_id) ON DELETE CASCADE,
    procedure_id INTEGER REFERENCES procedures(procedure_id) ON DELETE CASCADE,
    
    -- Fee Information
    fee_type VARCHAR(100), -- normal, tatkal, urgent, etc.
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    
    -- Applicability
    applicable_for TEXT, -- Description of when this fee applies
    validity_period VARCHAR(100),
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- USER INTERACTIONS & ANALYTICS
-- =====================================================

-- User Queries
CREATE TABLE IF NOT EXISTS user_queries (
    query_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    
    -- Query Information
    query_text TEXT NOT NULL,
    query_language VARCHAR(10) DEFAULT 'en',
    query_type VARCHAR(50), -- search, question, complaint
    
    -- Response Information
    response_text TEXT,
    response_quality_score DECIMAL(3,2), -- 0.00 to 1.00
    was_helpful BOOLEAN,
    
    -- Context
    service_id INTEGER REFERENCES services(service_id),
    procedure_id INTEGER REFERENCES procedures(procedure_id),
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100)
);

-- Search Analytics
CREATE TABLE IF NOT EXISTS search_analytics (
    search_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    
    -- Search Information
    search_query TEXT NOT NULL,
    search_language VARCHAR(10) DEFAULT 'en',
    search_filters JSONB,
    
    -- Results Information
    results_count INTEGER,
    results_returned INTEGER,
    search_time_ms INTEGER,
    
    -- User Information
    user_id INTEGER,
    session_id VARCHAR(100),
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SYSTEM & MONITORING
-- =====================================================

-- Data Quality Metrics
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    metric_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    
    -- Metric Information
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    metric_type VARCHAR(50), -- accuracy, completeness, freshness
    
    -- Context
    service_id INTEGER REFERENCES services(service_id),
    table_name VARCHAR(100),
    
    -- System Fields
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System Health
CREATE TABLE IF NOT EXISTS system_health (
    health_id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    
    -- Health Information
    component VARCHAR(100) NOT NULL, -- database, api, scraping, etc.
    status VARCHAR(20) NOT NULL, -- healthy, warning, critical
    message TEXT,
    
    -- Metrics
    response_time_ms INTEGER,
    error_count INTEGER,
    success_rate DECIMAL(5,2),
    
    -- System Fields
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Services indexes
CREATE INDEX IF NOT EXISTS idx_services_category ON services(category);
CREATE INDEX IF NOT EXISTS idx_services_active ON services(is_active);
CREATE INDEX IF NOT EXISTS idx_services_languages ON services USING GIN(languages_supported);

-- Procedures indexes
CREATE INDEX IF NOT EXISTS idx_procedures_service ON procedures(service_id);
CREATE INDEX IF NOT EXISTS idx_procedures_type ON procedures(procedure_type);
CREATE INDEX IF NOT EXISTS idx_procedures_language ON procedures(language);

-- Documents indexes
CREATE INDEX IF NOT EXISTS idx_documents_service ON documents(service_id);
CREATE INDEX IF NOT EXISTS idx_documents_procedure ON documents(procedure_id);
CREATE INDEX IF NOT EXISTS idx_documents_mandatory ON documents(is_mandatory);
CREATE INDEX IF NOT EXISTS idx_documents_processed ON documents(is_processed);
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);

-- FAQs indexes
CREATE INDEX IF NOT EXISTS idx_faqs_service ON faqs(service_id);
CREATE INDEX IF NOT EXISTS idx_faqs_procedure ON faqs(procedure_id);
CREATE INDEX IF NOT EXISTS idx_faqs_language ON faqs(language);
CREATE INDEX IF NOT EXISTS idx_faqs_question_embedding ON faqs USING ivfflat (question_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_faqs_answer_embedding ON faqs USING ivfflat (answer_embedding vector_cosine_ops);

-- Content chunks indexes
CREATE INDEX IF NOT EXISTS idx_content_chunks_content ON content_chunks(content_id);
CREATE INDEX IF NOT EXISTS idx_content_chunks_service ON content_chunks(service_id);
CREATE INDEX IF NOT EXISTS idx_content_chunks_embedding ON content_chunks USING ivfflat (embedding vector_cosine_ops);

-- Raw content indexes
CREATE INDEX IF NOT EXISTS idx_raw_content_source ON raw_content(source_type);
CREATE INDEX IF NOT EXISTS idx_raw_content_processed ON raw_content(is_processed);
CREATE INDEX IF NOT EXISTS idx_raw_content_language ON raw_content(language);

-- Offices indexes
CREATE INDEX IF NOT EXISTS idx_offices_service ON offices(service_id);
CREATE INDEX IF NOT EXISTS idx_offices_city ON offices(city);
CREATE INDEX IF NOT EXISTS idx_offices_state ON offices(state);
CREATE INDEX IF NOT EXISTS idx_offices_pincode ON offices(pincode);

-- User queries indexes
CREATE INDEX IF NOT EXISTS idx_user_queries_service ON user_queries(service_id);
CREATE INDEX IF NOT EXISTS idx_user_queries_language ON user_queries(query_language);
CREATE INDEX IF NOT EXISTS idx_user_queries_created ON user_queries(created_at);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables with updated_at
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_procedures_updated_at BEFORE UPDATE ON procedures FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_faqs_updated_at BEFORE UPDATE ON faqs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_offices_updated_at BEFORE UPDATE ON offices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fees_updated_at BEFORE UPDATE ON fees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_raw_content_updated_at BEFORE UPDATE ON raw_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Service Overview View
CREATE OR REPLACE VIEW service_overview AS
SELECT 
    s.service_id,
    s.name,
    s.category,
    s.ministry,
    s.is_active,
    s.is_online_available,
    s.is_api_available,
    s.languages_supported,
    COUNT(DISTINCT p.procedure_id) as procedure_count,
    COUNT(DISTINCT d.doc_id) as document_count,
    COUNT(DISTINCT f.faq_id) as faq_count,
    COUNT(DISTINCT o.office_id) as office_count
FROM services s
LEFT JOIN procedures p ON s.service_id = p.service_id
LEFT JOIN documents d ON s.service_id = d.service_id
LEFT JOIN faqs f ON s.service_id = f.service_id
LEFT JOIN offices o ON s.service_id = o.service_id
GROUP BY s.service_id, s.name, s.category, s.ministry, s.is_active, s.is_online_available, s.is_api_available, s.languages_supported;

-- Document Requirements View
CREATE OR REPLACE VIEW document_requirements AS
SELECT 
    d.doc_id,
    d.name,
    d.document_type,
    d.is_mandatory,
    d.copies_required,
    d.validity_period,
    s.name as service_name,
    s.category as service_category,
    p.title as procedure_title
FROM documents d
JOIN services s ON d.service_id = s.service_id
LEFT JOIN procedures p ON d.procedure_id = p.procedure_id
WHERE d.is_processed = TRUE;

-- =====================================================
-- INITIAL DATA SEEDING
-- =====================================================

-- Insert the 10 high-impact services
INSERT INTO services (name, short_name, description, category, ministry, department, authority, official_website, languages_supported) VALUES
('Passport Application/Renewal', 'passport', 'Passport services including new applications, renewals, and corrections', 'passport', 'Ministry of External Affairs', 'Passport Seva Kendra', 'MEA', 'https://passportindia.gov.in', ARRAY['en', 'hi']),
('Aadhaar Services', 'aadhaar', 'Aadhaar enrollment, updates, and verification services', 'aadhaar', 'Ministry of Electronics and IT', 'UIDAI', 'UIDAI', 'https://uidai.gov.in', ARRAY['en', 'hi']),
('PAN Card Services', 'pan', 'PAN card application, correction, and linking services', 'pan', 'Ministry of Finance', 'CBDT', 'Income Tax Department', 'https://incometax.gov.in', ARRAY['en', 'hi']),
('EPFO Services', 'epfo', 'EPF passbook, balance inquiry, and withdrawal services', 'epfo', 'Ministry of Labour', 'EPFO', 'EPFO', 'https://epfindia.gov.in', ARRAY['en', 'hi']),
('Ration Card Services', 'ration', 'Ration card application and management services', 'ration', 'Ministry of Consumer Affairs', 'FCS', 'State FCS Departments', 'https://nfsa.gov.in', ARRAY['en', 'hi']),
('Birth/Death Certificate', 'certificates', 'Birth and death certificate registration services', 'certificates', 'Ministry of Home Affairs', 'CRS', 'State Municipalities', 'https://crsorgi.gov.in', ARRAY['en', 'hi']),
('Driving License Services', 'driving', 'Driving license application, renewal, and related services', 'driving', 'Ministry of Road Transport', 'RTO', 'State Transport Departments', 'https://parivahan.gov.in', ARRAY['en', 'hi']),
('Voter ID Services', 'voter', 'Voter registration and EPIC card services', 'voter', 'Election Commission of India', 'CEO', 'State CEO Offices', 'https://nvsp.in', ARRAY['en', 'hi']),
('Scholarship Portals', 'scholarship', 'Educational scholarship application and management', 'scholarship', 'Ministry of Education', 'NSP', 'State Education Departments', 'https://scholarships.gov.in', ARRAY['en', 'hi']),
('Grievance Redressal', 'grievance', 'Citizen grievance filing and tracking services', 'grievance', 'Department of Administrative Reforms', 'DARPG', 'CPGRAMS', 'https://pgportal.gov.in', ARRAY['en', 'hi'])
ON CONFLICT DO NOTHING;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE services IS 'Core government services information';
COMMENT ON TABLE procedures IS 'Step-by-step procedures for each service';
COMMENT ON TABLE documents IS 'Document requirements and processed content';
COMMENT ON TABLE faqs IS 'Frequently asked questions and answers';
COMMENT ON TABLE raw_content IS 'Raw scraped and ingested content';
COMMENT ON TABLE content_chunks IS 'Text chunks for vector search';
COMMENT ON TABLE offices IS 'Government office locations and contact info';
COMMENT ON TABLE fees IS 'Fee structure for different services';
COMMENT ON TABLE user_queries IS 'User search queries and interactions';
COMMENT ON TABLE search_analytics IS 'Search performance analytics';
COMMENT ON TABLE data_quality_metrics IS 'Data quality monitoring metrics';
COMMENT ON TABLE system_health IS 'System health monitoring data';
