-- Supabase Database Schema for Tymon AI Chatbot
-- Run this in Supabase SQL Editor to create the tables

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Memories table
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    importance_score FLOAT NOT NULL DEFAULT 0.5 CHECK (importance_score >= 0 AND importance_score <= 1),
    category TEXT NOT NULL DEFAULT 'other',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    decay_score FLOAT NOT NULL DEFAULT 0.5 CHECK (decay_score >= 0 AND decay_score <= 1),
    ttl_days INTEGER NOT NULL DEFAULT 180,
    last_used_in_chat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_pinned BOOLEAN NOT NULL DEFAULT FALSE,
    memory_type TEXT NOT NULL DEFAULT 'fact',
    source TEXT NOT NULL DEFAULT 'chat'
);

-- User journals table
CREATE TABLE IF NOT EXISTS user_journals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[]
);

-- Pinned conversations table (for pin state per user)
CREATE TABLE IF NOT EXISTS pinned_conversations (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id TEXT NOT NULL,
    pinned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, conversation_id)
);

-- AI journals table
CREATE TABLE IF NOT EXISTS ai_journals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID,
    reflection TEXT NOT NULL,
    learnings TEXT[] DEFAULT ARRAY[]::TEXT[],
    questions_raised TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance_score DESC);
CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
CREATE INDEX IF NOT EXISTS idx_memories_memory_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_decay ON memories(decay_score DESC);
CREATE INDEX IF NOT EXISTS idx_memories_last_used ON memories(last_used_in_chat DESC);
CREATE INDEX IF NOT EXISTS idx_user_journals_user_id ON user_journals(user_id);
CREATE INDEX IF NOT EXISTS idx_user_journals_created_at ON user_journals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_journals_user_id ON ai_journals(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_journals_created_at ON ai_journals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pinned_conversations_user_id ON pinned_conversations(user_id);

-- Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_journals ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_journals ENABLE ROW LEVEL SECURITY;
ALTER TABLE pinned_conversations ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (adjust based on your auth setup)
-- For now, allow all operations - you should restrict based on user_id matching authenticated user
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (true);
CREATE POLICY "Users can insert own data" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can view own conversations" ON conversations FOR SELECT USING (true);
CREATE POLICY "Users can insert own conversations" ON conversations FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can delete own conversations" ON conversations FOR DELETE USING (true);
CREATE POLICY "Users can view own memories" ON memories FOR SELECT USING (true);
CREATE POLICY "Users can insert own memories" ON memories FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can delete own memories" ON memories FOR DELETE USING (true);
CREATE POLICY "Users can view own journals" ON user_journals FOR SELECT USING (true);
CREATE POLICY "Users can insert own journals" ON user_journals FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update own journals" ON user_journals FOR UPDATE USING (true);
CREATE POLICY "Users can delete own journals" ON user_journals FOR DELETE USING (true);
CREATE POLICY "Users can view own AI journals" ON ai_journals FOR SELECT USING (true);
CREATE POLICY "AI can insert journals" ON ai_journals FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can view own pinned" ON pinned_conversations FOR SELECT USING (true);
CREATE POLICY "Users can insert own pinned" ON pinned_conversations FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update own pinned" ON pinned_conversations FOR UPDATE USING (true);
CREATE POLICY "Users can delete own pinned" ON pinned_conversations FOR DELETE USING (true);