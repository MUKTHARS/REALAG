-- Create database
CREATE DATABASE realestate_db;

-- Connect to database
\c realestate_db;

-- Create tables (these will be created by SQLAlchemy, but here's the SQL for reference)
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    price DECIMAL,
    location VARCHAR,
    property_type VARCHAR,
    bedrooms INTEGER,
    bathrooms INTEGER,
    area_sqft DECIMAL,
    amenities JSONB,
    images JSONB,
    available_from TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    user_message TEXT,
    agent_response TEXT,
    language VARCHAR DEFAULT 'english',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    conversation_data JSONB
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    budget_min DECIMAL,
    budget_max DECIMAL,
    preferred_locations JSONB,
    property_types JSONB,
    bedrooms INTEGER,
    amenities JSONB,
    language VARCHAR DEFAULT 'english',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(location);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_property_type ON properties(property_type);

-- Insert sample properties
INSERT INTO properties (title, description, price, location, property_type, bedrooms, bathrooms, area_sqft, amenities, images) VALUES
('Luxury Apartment in Downtown Dubai', 'Beautiful 2-bedroom apartment with Burj Khalifa view', 2500000, 'Downtown Dubai', 'apartment', 2, 2, 1800, '["pool", "gym", "parking", "security"]', '[]'),
('Modern Villa in Palm Jumeirah', 'Spacious 4-bedroom villa with private beach access', 8500000, 'Palm Jumeirah', 'villa', 4, 5, 4500, '["private beach", "pool", "garden", "maid room"]', '[]'),
('Affordable Studio in Deira', 'Cozy studio apartment near metro station', 350000, 'Deira', 'apartment', 1, 1, 600, '["metro access", "parking", "security"]', '[]'),
('Luxury Penthouse in Business Bay', 'Stunning 3-bedroom penthouse with city views', 5200000, 'Business Bay', 'apartment', 3, 3, 3200, '["pool", "gym", "concierge", "private elevator"]', '[]');