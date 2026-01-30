import { useState, useEffect } from 'react'
import { chatAPI, ConversationSummary } from '../../services/api'
import './ConversationList.css'

interface ConversationListProps {
  userId: string
  currentConversationId?: string
  onSelectConversation: (conversationId: string | undefined) => void
  onNewConversation: () => void
  onMenuClick?: () => void
}

const ConversationList = ({
  userId,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onMenuClick,
}: ConversationListProps) => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadConversations()
  }, [userId])

  useEffect(() => {
    if (currentConversationId) {
      loadConversations()
    }
  }, [currentConversationId])

  const loadConversations = async () => {
    setIsLoading(true)
    try {
      const data = await chatAPI.getConversations(userId)
      setConversations(data)
    } catch (error) {
      console.error('Failed to load conversations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="conversation-list">
      <div className="conversation-list-topbar">
        <button
          type="button"
          className="conversation-list-icon-btn"
          onClick={onMenuClick}
          aria-label="Menu"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <button
          type="button"
          className="conversation-list-icon-btn"
          aria-label="Tìm kiếm"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </button>
      </div>

      <button type="button" className="new-conversation-btn" onClick={onNewConversation}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
        </svg>
        <span>Cuộc trò chuyện mới</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" strokeDasharray="4 2" />
        </svg>
      </button>

      <h3 className="conversation-list-title">Cuộc trò chuyện</h3>

      <div className="conversation-list-content">
        {isLoading ? (
          <div className="conversation-loading">Đang tải...</div>
        ) : conversations.length === 0 ? (
          <div className="conversation-empty">Chưa có cuộc trò chuyện nào</div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.conversation_id}
              className={`conversation-item ${
                currentConversationId === conv.conversation_id ? 'active' : ''
              }`}
              onClick={() => onSelectConversation(conv.conversation_id)}
            >
              <span className="conversation-item-title">{conv.first_message || 'Cuộc trò chuyện mới'}</span>
              <button
                type="button"
                className="conversation-item-pin"
                aria-label="Ghim"
                onClick={(e) => e.stopPropagation()}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2v6l4 4v6h-2v-6l-2-2-2 2v6H8v-6l4-4V2z" />
                </svg>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ConversationList
