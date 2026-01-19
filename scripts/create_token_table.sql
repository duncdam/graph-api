-- Create tokens table
CREATE TABLE IF NOT EXISTS access_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    token_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    scopes TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    username VARCHAR(100) NOT NULL,
    full_name VARCHAR(255),
    email VARCHAR(255),
    created_by VARCHAR(100),
    last_used TIMESTAMP WITH TIME ZONE,
    use_count INTEGER DEFAULT 0
);

-- Create index for faster token lookups
CREATE INDEX IF NOT EXISTS idx_access_tokens_token ON access_tokens(token);
CREATE INDEX IF NOT EXISTS idx_access_tokens_token_id ON access_tokens(token_id);
CREATE INDEX IF NOT EXISTS idx_access_tokens_active ON access_tokens(is_active);
CREATE INDEX IF NOT EXISTS idx_access_tokens_expires ON access_tokens(expires_at);

-- Create a view for active tokens
CREATE OR REPLACE VIEW active_tokens AS
SELECT * FROM access_tokens 
WHERE is_active = TRUE 
AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP);