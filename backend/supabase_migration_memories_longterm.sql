-- Migration: add long-term memory fields to memories table
ALTER TABLE memories
    ADD COLUMN IF NOT EXISTS decay_score FLOAT NOT NULL DEFAULT 0.5 CHECK (decay_score >= 0 AND decay_score <= 1),
    ADD COLUMN IF NOT EXISTS ttl_days INTEGER NOT NULL DEFAULT 180,
    ADD COLUMN IF NOT EXISTS last_used_in_chat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS memory_type TEXT NOT NULL DEFAULT 'fact',
    ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'chat';

CREATE INDEX IF NOT EXISTS idx_memories_memory_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_decay ON memories(decay_score DESC);
CREATE INDEX IF NOT EXISTS idx_memories_last_used ON memories(last_used_in_chat DESC);
