-- Migration: Add pinned_conversations table and DELETE policy for conversations
-- Run this if you already have the base schema applied

-- Pinned conversations table
CREATE TABLE IF NOT EXISTS pinned_conversations (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id TEXT NOT NULL,
    pinned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, conversation_id)
);

CREATE INDEX IF NOT EXISTS idx_pinned_conversations_user_id ON pinned_conversations(user_id);

ALTER TABLE pinned_conversations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own pinned" ON pinned_conversations;
DROP POLICY IF EXISTS "Users can insert own pinned" ON pinned_conversations;
DROP POLICY IF EXISTS "Users can update own pinned" ON pinned_conversations;
DROP POLICY IF EXISTS "Users can delete own pinned" ON pinned_conversations;
CREATE POLICY "Users can view own pinned" ON pinned_conversations FOR SELECT USING (true);
CREATE POLICY "Users can insert own pinned" ON pinned_conversations FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update own pinned" ON pinned_conversations FOR UPDATE USING (true);
CREATE POLICY "Users can delete own pinned" ON pinned_conversations FOR DELETE USING (true);

-- Allow delete on conversations
DROP POLICY IF EXISTS "Users can delete own conversations" ON conversations;
CREATE POLICY "Users can delete own conversations" ON conversations FOR DELETE USING (true);
