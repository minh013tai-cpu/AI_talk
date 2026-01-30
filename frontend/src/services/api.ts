import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL, '-> API_BASE_URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Log backend error detail when response is 5xx (so you see it in Console)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status && err.response.status >= 500) {
      const data = err.response?.data
      const detail = data != null && typeof data === 'object' && 'detail' in data ? data.detail : data
      console.error('[API 5xx]', err.config?.url, '-> Backend error detail:', detail ?? '(no body)')
    }
    return Promise.reject(err)
  }
)

export interface ChatMessage {
  message: string
  user_id: string
  conversation_id?: string
}

export interface ChatResponse {
  response: string
  conversation_id: string
  timestamp: string
}

export interface Conversation {
  id: string
  user_id: string
  message: string
  response: string
  timestamp: string
  metadata?: any
}

export interface Memory {
  id: string
  user_id: string
  content: string
  importance_score: number
  category: string
  created_at: string
  last_accessed: string
  access_count: number
}

export interface UserJournal {
  id: string
  user_id: string
  content: string
  created_at: string
  tags?: string[]
}

export interface AIJournal {
  id: string
  user_id: string
  conversation_id: string
  reflection: string
  learnings: string[]
  questions_raised: string[]
  created_at: string
}

export interface ConversationSummary {
  conversation_id: string
  first_message: string
  last_message_time: string
  message_count: number
  pinned?: boolean
}

// Chat API
export const chatAPI = {
  sendMessage: async (message: ChatMessage): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/api/chat/', message)
    return response.data
  },
  
  getHistory: async (userId: string, conversationId?: string, limit: number = 50): Promise<Conversation[]> => {
    const response = await api.get<Conversation[]>(`/api/chat/history/${userId}`, {
      params: { conversation_id: conversationId, limit },
    })
    return response.data
  },
  
  getConversations: async (userId: string): Promise<ConversationSummary[]> => {
    const response = await api.get<ConversationSummary[]>(`/api/chat/conversations/${userId}`)
    const data = response.data
    return Array.isArray(data) ? data : []
  },

  deleteConversation: async (userId: string, conversationId: string): Promise<void> => {
    await api.delete(`/api/chat/conversations/${userId}/${conversationId}`)
  },

  pinConversation: async (userId: string, conversationId: string): Promise<void> => {
    await api.post(`/api/chat/conversations/${userId}/${conversationId}/pin`)
  },

  unpinConversation: async (userId: string, conversationId: string): Promise<void> => {
    await api.delete(`/api/chat/conversations/${userId}/${conversationId}/pin`)
  },
}

// Memory API
export const memoryAPI = {
  getAll: async (userId: string): Promise<Memory[]> => {
    const response = await api.get<Memory[]>(`/api/memory/${userId}`)
    return response.data
  },
  
  getRelevant: async (userId: string, query: string, limit: number = 5) => {
    const response = await api.get(`/api/memory/${userId}/relevant`, {
      params: { query, limit },
    })
    return response.data
  },
  
  delete: async (memoryId: string, userId: string): Promise<void> => {
    await api.delete(`/api/memory/${memoryId}`, {
      params: { user_id: userId },
    })
  },
}

// Journal API
export const journalAPI = {
  // User journals
  createUserJournal: async (data: {
    user_id: string
    content: string
    tags?: string[]
  }): Promise<UserJournal> => {
    const response = await api.post<UserJournal>('/api/journal/user', data)
    return response.data
  },
  
  getUserJournals: async (
    userId: string,
    limit: number = 50,
    offset: number = 0,
    tags?: string
  ): Promise<UserJournal[]> => {
    const response = await api.get<UserJournal[]>(`/api/journal/user/${userId}`, {
      params: { limit, offset, tags },
    })
    return response.data
  },
  
  searchUserJournals: async (userId: string, query: string): Promise<UserJournal[]> => {
    const response = await api.get<UserJournal[]>(`/api/journal/user/${userId}/search`, {
      params: { q: query },
    })
    return response.data
  },
  
  updateUserJournal: async (
    journalId: string,
    userId: string,
    content: string,
    tags?: string[]
  ): Promise<UserJournal> => {
    const response = await api.put<UserJournal>(
      `/api/journal/user/entry/${journalId}`,
      { content, tags: tags?.join(',') },
      { params: { user_id: userId } }
    )
    return response.data
  },
  
  deleteUserJournal: async (journalId: string, userId: string): Promise<void> => {
    await api.delete(`/api/journal/user/entry/${journalId}`, {
      params: { user_id: userId },
    })
  },
  
  // AI journals
  getAIJournals: async (
    userId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<AIJournal[]> => {
    const response = await api.get<AIJournal[]>(`/api/journal/ai/${userId}`, {
      params: { limit, offset },
    })
    return response.data
  },
  
  getAIJournal: async (journalId: string, userId: string): Promise<AIJournal> => {
    const response = await api.get<AIJournal>(`/api/journal/ai/entry/${journalId}`, {
      params: { user_id: userId },
    })
    return response.data
  },
}
