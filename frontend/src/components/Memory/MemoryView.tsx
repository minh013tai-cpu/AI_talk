import { useState, useEffect } from 'react'
import { memoryAPI, Memory } from '../../services/api'
import './MemoryView.css'

const DEMO_USER_ID = '00000000-0000-0000-0000-000000000000'

const MemoryView = () => {
  const [memories, setMemories] = useState<Memory[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all')

  useEffect(() => {
    loadMemories()
  }, [])

  const loadMemories = async () => {
    setIsLoading(true)
    try {
      const data = await memoryAPI.getAll(DEMO_USER_ID)
      setMemories(data)
    } catch (error) {
      console.error('Failed to load memories:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (memoryId: string) => {
    if (!confirm('Are you sure you want to delete this memory?')) return

    try {
      await memoryAPI.delete(memoryId, DEMO_USER_ID)
      loadMemories()
    } catch (error) {
      console.error('Failed to delete memory:', error)
    }
  }

  const getImportanceLabel = (score: number): string => {
    if (score >= 0.7) return 'High'
    if (score >= 0.4) return 'Medium'
    return 'Low'
  }

  const formatTTL = (ttl?: number): string => {
    if (!ttl) return 'n/a'
    return `${ttl}d`
  }

  const getImportanceColor = (score: number): string => {
    if (score >= 0.7) return '#4caf50'
    if (score >= 0.4) return '#ff9800'
    return '#999'
  }

  const filteredMemories = memories.filter((mem) => {
    if (filter === 'all') return true
    if (filter === 'high') return mem.importance_score >= 0.7
    if (filter === 'medium') return mem.importance_score >= 0.4 && mem.importance_score < 0.7
    return mem.importance_score < 0.4
  })

  return (
    <div className="memory-view">
      <div className="memory-header">
        <h2>Memories</h2>
        <p className="memory-subtitle">
          Important information Tymon remembers about you
        </p>
      </div>

      <div className="memory-filters">
        <button
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button
          className={filter === 'high' ? 'active' : ''}
          onClick={() => setFilter('high')}
        >
          High Importance
        </button>
        <button
          className={filter === 'medium' ? 'active' : ''}
          onClick={() => setFilter('medium')}
        >
          Medium
        </button>
        <button
          className={filter === 'low' ? 'active' : ''}
          onClick={() => setFilter('low')}
        >
          Low
        </button>
      </div>

      {isLoading ? (
        <p>Loading memories...</p>
      ) : filteredMemories.length === 0 ? (
        <div className="empty-state">
          <p>No memories yet.</p>
          <p className="empty-hint">
            Start chatting with Tymon to build memories!
          </p>
        </div>
      ) : (
        <div className="memories-grid">
          {filteredMemories.map((memory) => (
            <div key={memory.id} className="memory-card">
              <div className="memory-header-card">
                <div className="memory-badges">
                  <div className="memory-category">{memory.category}</div>
                  {memory.memory_type && (
                    <div className="memory-type">{memory.memory_type}</div>
                  )}
                  {memory.is_pinned && <div className="memory-pinned">Pinned</div>}
                </div>
                <div
                  className="memory-importance"
                  style={{ color: getImportanceColor(memory.importance_score) }}
                >
                  {getImportanceLabel(memory.importance_score)}
                </div>
              </div>
              <div className="memory-content">{memory.content}</div>
              <div className="memory-footer">
                <div className="memory-stats">
                  <span>Accessed {memory.access_count} times</span>
                  {memory.last_accessed && (
                    <span>
                      Last: {new Date(memory.last_accessed).toLocaleDateString()}
                    </span>
                  )}
                  <span>TTL: {formatTTL(memory.ttl_days)}</span>
                  {typeof memory.decay_score === 'number' && (
                    <span>Decay: {memory.decay_score.toFixed(2)}</span>
                  )}
                  {memory.source && <span>Source: {memory.source}</span>}
                </div>
                <button
                  className="delete-button"
                  onClick={() => memory.id && handleDelete(memory.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MemoryView
