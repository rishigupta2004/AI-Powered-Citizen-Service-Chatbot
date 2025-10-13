-- citizens table schema
CREATE TABLE IF NOT EXISTS citizens (
    id BIGSERIAL PRIMARY KEY,
    uid VARCHAR(12) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    age INTEGER NOT NULL,
    address TEXT NOT NULL,
    pincode VARCHAR(6) NOT NULL,
    state VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_citizens_uid ON citizens(uid);
CREATE INDEX IF NOT EXISTS idx_citizens_email ON citizens(email);
CREATE INDEX IF NOT EXISTS idx_citizens_pincode ON citizens(pincode);
CREATE INDEX IF NOT EXISTS idx_citizens_state ON citizens(state);