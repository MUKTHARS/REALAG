-- Create database
CREATE DATABASE realestate_db;

-- Connect to database
\c realestate_db;

-- Create tables
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

-- NEW: Chat sessions table for sidebar
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR UNIQUE NOT NULL,
    title VARCHAR NOT NULL,
    language VARCHAR DEFAULT 'english',
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(location);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_property_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_is_active ON chat_sessions(is_active);

-- Insert sample properties
INSERT INTO properties (title, description, price, location, property_type, bedrooms, bathrooms, area_sqft, amenities, images) VALUES
('Luxury Apartment in Downtown Dubai', 'Beautiful 2-bedroom apartment with Burj Khalifa view', 2500000, 'Downtown Dubai', 'apartment', 2, 2, 1800, '["pool", "gym", "parking", "security"]', '[]'),
('Modern Villa in Palm Jumeirah', 'Spacious 4-bedroom villa with private beach access', 8500000, 'Palm Jumeirah', 'villa', 4, 5, 4500, '["private beach", "pool", "garden", "maid room"]', '[]'),
('Affordable Studio in Deira', 'Cozy studio apartment near metro station', 350000, 'Deira', 'apartment', 1, 1, 600, '["metro access", "parking", "security"]', '[]'),
('Luxury Penthouse in Business Bay', 'Stunning 3-bedroom penthouse 
with city views', 5200000, 'Business Bay', 'apartment', 3, 3, 3200, '["pool", "gym", "concierge", "private elevator"]', '[]');


CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    hashed_password VARCHAR,
    is_oauth BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add user_id to conversations and chat_sessions
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Create indexes for user relationships
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Update existing chat_sessions to have NULL user_id for old data
UPDATE chat_sessions SET user_id = NULL WHERE user_id IS NULL;

-- Update existing conversations to have NULL user_id for old data  
UPDATE conversations SET user_id = NULL WHERE user_id IS NULL;

-- Add constraints to ensure data integrity
ALTER TABLE chat_sessions ALTER COLUMN user_id SET DEFAULT NULL;
ALTER TABLE conversations ALTER COLUMN user_id SET DEFAULT NULL;