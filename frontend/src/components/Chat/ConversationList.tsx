import { useState, useEffect } from 'react'
import { chatAPI, ConversationSummary } from '../../services/api'
import './ConversationList.css'

interface ConversationListProps {
  userId: string
  currentConversationId?: string
  onSelectConversation: (conversationId: string | undefined) => void
  onNewConversation: () => void
}

const ConversationList = ({
  userId,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays === 1) {
      return 'Hôm qua'
    } else if (diffDays < 7) {
      return `${diffDays} ngày trước`
    } else {
      return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })
    }
  }

  return (
    <div className="conversation-list">
      <div className="conversation-list-header">
        <h3>Cuộc trò chuyện</h3>
        <button className="new-conversation-btn" onClick={onNewConversation} title="Tạo cuộc trò chuyện mới">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
      </div>

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
              <div className="conversation-item-content">
                <div className="conversation-item-title">{conv.first_message || 'Cuộc trò chuyện mới'}</div>
                <div className="conversation-item-meta">
                  <span className="conversation-item-count">{conv.message_count} tin nhắn</span>
                  <span className="conversation-item-time">{formatDate(conv.last_message_time)}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ConversationList
