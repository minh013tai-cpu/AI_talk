import { useState, useCallback } from 'react'
import { chatAPI, Conversation, ChatResponse } from '../services/api'

interface UseChatReturn {
  messages: Conversation[]
  isLoading: boolean
  error: string | null
  currentConversationId: string | undefined
  sendMessage: (message: string, userId: string, conversationId?: string) => Promise<void>
  loadHistory: (userId: string, conversationId?: string) => Promise<void>
  setConversationId: (conversationId: string | undefined) => void
  clearError: () => void
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>()

  const sendMessage = useCallback(async (
    message: string,
    userId: string,
    conversationId?: string
  ) => {
    if (!message.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const response: ChatResponse = await chatAPI.sendMessage({
        message: message.trim(),
        user_id: userId,
        conversation_id: conversationId,
      })

      // Add user message and AI response to messages
      const userMessage: Conversation = {
        id: `user-${Date.now()}`,
        user_id: userId,
        message: message.trim(),
        response: '',
        timestamp: new Date().toISOString(),
      }

      const aiResponse: Conversation = {
        id: `ai-${Date.now()}`,
        user_id: userId,
        message: message.trim(),
        response: response.response,
        timestamp: response.timestamp,
        metadata: { conversation_id: response.conversation_id },
      }

      setMessages((prev) => [...prev, userMessage, aiResponse])
      
      if (response.conversation_id) {
        setCurrentConversationId(response.conversation_id)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to send message')
      console.error('Chat error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const loadHistory = useCallback(async (userId: string, conversationId?: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const history = await chatAPI.getHistory(userId, conversationId)
      const expanded: Conversation[] = []
      for (const row of history) {
        expanded.push({
          id: `${row.id}-user`,
          user_id: row.user_id,
          message: row.message,
          response: '',
          timestamp: row.timestamp,
        })
        expanded.push({
          id: `${row.id}-ai`,
          user_id: row.user_id,
          message: row.message,
          response: row.response,
          timestamp: row.timestamp,
          metadata: row.metadata,
        })
      }
      setMessages(expanded)
      if (conversationId) {
        setCurrentConversationId(conversationId)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load history')
      console.error('Load history error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const setConversationId = useCallback((conversationId: string | undefined) => {
    setCurrentConversationId(conversationId)
    setMessages([])
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    currentConversationId,
    sendMessage,
    loadHistory,
    setConversationId,
    clearError,
  }
}
