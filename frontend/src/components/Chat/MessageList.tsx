import { Conversation } from '../../services/api'
import './MessageList.css'

interface MessageListProps {
  messages: Conversation[]
  isLoading: boolean
}

const MessageList = ({ messages, isLoading }: MessageListProps) => {
  return (
    <div className="message-list">
      {messages.length === 0 && !isLoading && (
        <div className="empty-state">
          <div className="empty-state-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" />
            </svg>
          </div>
          <p className="empty-state-greeting">Xin chào! Chúng ta nên bắt đầu từ đâu nhỉ?</p>
        </div>
      )}

      {messages.map((msg, index) => {
        const isUser = !msg.response || msg.response.trim() === ''
        const displayText = isUser ? msg.message : msg.response

        return (
          <div key={msg.id || index} className={`message ${isUser ? 'user-message' : 'ai-message'}`}>
            <div className="message-avatar">
              {isUser ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-text">
                {displayText}
              </div>
              <div className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        )
      })}

      {isLoading && (
        <div className="message ai-message">
          <div className="message-avatar">🤖</div>
          <div className="message-content">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MessageList
