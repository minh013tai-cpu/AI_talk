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
          <p>Start a conversation with Tymon!</p>
          <p className="empty-hint">Tymon can remember important details, ask clarifying questions, and have thoughtful conversations.</p>
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
