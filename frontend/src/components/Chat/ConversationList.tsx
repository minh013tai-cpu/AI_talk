import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { chatAPI, ConversationSummary } from '../../services/api'
import './ConversationList.css'

interface ConversationListProps {
  userId: string
  currentConversationId?: string
  onSelectConversation: (conversationId: string | undefined) => void
  onNewConversation: () => void
  onMenuClick?: () => void
}

interface MenuPosition {
  top: number
  left: number
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
  const [openMenuId, setOpenMenuId] = useState<string | null>(null)
  const [menuPosition, setMenuPosition] = useState<MenuPosition | null>(null)

  useEffect(() => {
    loadConversations()
  }, [userId])

  useEffect(() => {
    if (currentConversationId) {
      loadConversations()
    }
  }, [currentConversationId])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (target.closest('[data-conversation-menu]') || target.closest('[data-conversation-dropdown]')) {
        return
      }
      setOpenMenuId(null)
      setMenuPosition(null)
    }
    if (openMenuId) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [openMenuId])

  const safeConversations = Array.isArray(conversations) ? conversations : []

  const loadConversations = async () => {
    setIsLoading(true)
    try {
      const data = await chatAPI.getConversations(userId)
      setConversations(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Failed to load conversations:', error)
      setConversations([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleTogglePin = async (e: React.MouseEvent, conv: ConversationSummary) => {
    e.stopPropagation()
    setOpenMenuId(null)
    setMenuPosition(null)
    try {
      if (conv.pinned) {
        await chatAPI.unpinConversation(userId, conv.conversation_id)
      } else {
        await chatAPI.pinConversation(userId, conv.conversation_id)
      }
      await loadConversations()
    } catch (err) {
      console.error('Failed to toggle pin:', err)
    }
  }

  const handleDelete = async (e: React.MouseEvent, conv: ConversationSummary) => {
    e.stopPropagation()
    setOpenMenuId(null)
    setMenuPosition(null)
    try {
      await chatAPI.deleteConversation(userId, conv.conversation_id)
      if (currentConversationId === conv.conversation_id) {
        onSelectConversation(undefined)
      }
      await loadConversations()
    } catch (err) {
      console.error('Failed to delete conversation:', err)
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
        ) : safeConversations.length === 0 ? (
          <div className="conversation-empty">Chưa có cuộc trò chuyện nào</div>
        ) : (
          safeConversations.map((conv) => (
            <div
              key={conv.conversation_id}
              className={`conversation-item ${
                currentConversationId === conv.conversation_id ? 'active' : ''
              }`}
              onClick={(e) => {
                const t = e.target as HTMLElement
                if (t.closest('[data-conversation-menu]')) return
                if (t.closest('.conversation-item-title')) return
                onSelectConversation(conv.conversation_id)
              }}
            >
              {conv.pinned && (
                <span className="conversation-item-pinned-icon" aria-hidden="true">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2v6l4 4v6h-2v-6l-2-2-2 2v6H8v-6l4-4V2z" />
                  </svg>
                </span>
              )}
              <span
                className="conversation-item-title"
                role="button"
                tabIndex={0}
                onClick={(e) => {
                  e.stopPropagation()
                  onSelectConversation(conv.conversation_id)
                }}
                onKeyDown={(e) => e.key === 'Enter' && onSelectConversation(conv.conversation_id)}
              >
                {conv.first_message || 'Cuộc trò chuyện mới'}
              </span>
              <div
                className="conversation-item-menu-zone"
                data-conversation-menu
                role="button"
                tabIndex={0}
                aria-label="Tùy chọn"
                aria-haspopup="menu"
                aria-expanded={openMenuId === conv.conversation_id}
                onClick={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
                  if (openMenuId === conv.conversation_id) {
                    setOpenMenuId(null)
                    setMenuPosition(null)
                  } else {
                    setOpenMenuId(conv.conversation_id)
                    setMenuPosition({ top: rect.top, left: rect.right + 4 })
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    e.stopPropagation()
                    const el = e.currentTarget as HTMLElement
                    const rect = el.getBoundingClientRect()
                    if (openMenuId === conv.conversation_id) {
                      setOpenMenuId(null)
                      setMenuPosition(null)
                    } else {
                      setOpenMenuId(conv.conversation_id)
                      setMenuPosition({ top: rect.top, left: rect.right + 4 })
                    }
                  }
                }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <circle cx="12" cy="5" r="2" />
                  <circle cx="12" cy="12" r="2" />
                  <circle cx="12" cy="19" r="2" />
                </svg>
              </div>
            </div>
          ))
        )}
      </div>

      {openMenuId && menuPosition && (() => {
        const conv = safeConversations.find((c) => c.conversation_id === openMenuId)
        if (!conv) return null
        return createPortal(
          <div
            className="conversation-dropdown conversation-dropdown-portal"
            data-conversation-dropdown
            style={{ top: menuPosition.top, left: menuPosition.left }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              className="conversation-dropdown-item"
              onClick={(e) => handleTogglePin(e, conv)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2v6l4 4v6h-2v-6l-2-2-2 2v6H8v-6l4-4V2z" />
              </svg>
              <span>{conv.pinned ? 'Bỏ ghim' : 'Ghim'}</span>
            </button>
            <button
              type="button"
              className="conversation-dropdown-item conversation-dropdown-item-danger"
              onClick={(e) => handleDelete(e, conv)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                <line x1="10" y1="11" x2="10" y2="17" />
                <line x1="14" y1="11" x2="14" y2="17" />
              </svg>
              <span>Xoá</span>
            </button>
          </div>,
          document.body
        )
      })()}
    </div>
  )
}

export default ConversationList
