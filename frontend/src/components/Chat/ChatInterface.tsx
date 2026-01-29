import { useEffect, useRef } from 'react'
import { useChat } from '../../hooks/useChat'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import ConversationList from './ConversationList'
import './ChatInterface.css'

const DEMO_USER_ID = '00000000-0000-0000-0000-000000000000'

const ChatInterface = () => {
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
    <div className="chat-interface-container">
      <ConversationList
        userId={DEMO_USER_ID}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
      />
      <div className="chat-interface">
        <div className="chat-header">
          <h2>Chat with Tymon</h2>
          <p className="chat-subtitle">Your personalized AI assistant</p>
        </div>

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
