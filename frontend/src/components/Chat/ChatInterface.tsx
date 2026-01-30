import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useChat } from '../../hooks/useChat'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import ConversationList from './ConversationList'
import './ChatInterface.css'

const DEMO_USER_ID = '00000000-0000-0000-0000-000000000000'

const ChatInterface = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const {
    messages,
    isLoading,
    error,
    currentConversationId,
    sendMessage,
    loadHistory,
    setConversationId,
    clearError,
  } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (currentConversationId) {
      loadHistory(DEMO_USER_ID, currentConversationId)
    }
  }, [currentConversationId, loadHistory])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (message: string) => {
    await sendMessage(message, DEMO_USER_ID, currentConversationId)
  }

  const handleSelectConversation = (conversationId: string | undefined) => {
    setConversationId(conversationId)
  }

  const handleNewConversation = () => {
    setConversationId(undefined)
  }

  return (
    <div className={`chat-interface-container ${sidebarOpen ? 'sidebar-open' : ''}`}>
      <div className="conversation-list-wrapper">
        <ConversationList
          userId={DEMO_USER_ID}
          currentConversationId={currentConversationId}
          onSelectConversation={(id) => {
            handleSelectConversation(id)
            setSidebarOpen(false)
          }}
          onNewConversation={() => {
            handleNewConversation()
            setSidebarOpen(false)
          }}
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        />
      </div>
      <button
        type="button"
        className="sidebar-toggle-overlay"
        aria-label="Đóng sidebar"
        onClick={() => setSidebarOpen(false)}
      />
      <div className="chat-interface">
        <header className="chat-main-header">
          <button
            type="button"
            className="sidebar-toggle-btn"
            aria-label="Mở menu"
            onClick={() => setSidebarOpen(true)}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
          <h1>Tymon AI</h1>
          <nav>
            <Link to="/">Chat</Link>
            <Link to="/journal">Journal</Link>
            <Link to="/memory">Memories</Link>
          </nav>
        </header>

        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button onClick={clearError}>×</button>
          </div>
        )}

        <MessageList messages={messages} isLoading={isLoading} />

        <MessageInput onSend={handleSend} disabled={isLoading} />

        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}

export default ChatInterface
