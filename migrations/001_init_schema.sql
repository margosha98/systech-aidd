-- Initial schema for systech-aidd
-- Migration: 001_init_schema

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    content_length INTEGER NOT NULL,
    username VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- Index for efficient queries: filter by chat/user, exclude deleted, sort by date
CREATE INDEX IF NOT EXISTS idx_chat_user_active 
ON messages (chat_id, user_id, is_deleted, created_at DESC);

-- Index for searching by username (useful for analytics)
CREATE INDEX IF NOT EXISTS idx_messages_username 
ON messages (username);

