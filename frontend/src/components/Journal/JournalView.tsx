import { useState, useEffect } from 'react'
import { journalAPI, UserJournal, AIJournal } from '../../services/api'
import JournalEntry from './JournalEntry'
import './JournalView.css'

const DEMO_USER_ID = '00000000-0000-0000-0000-000000000000'

const JournalView = () => {
  const [userJournals, setUserJournals] = useState<UserJournal[]>([])
  const [aiJournals, setAIJournals] = useState<AIJournal[]>([])
  const [activeTab, setActiveTab] = useState<'user' | 'ai'>('user')
  const [isLoading, setIsLoading] = useState(false)
  const [newEntry, setNewEntry] = useState('')
  const [tags, setTags] = useState('')

  useEffect(() => {
    loadJournals()
  }, [])

  const loadJournals = async () => {
    setIsLoading(true)
    try {
      const [user, ai] = await Promise.all([
        journalAPI.getUserJournals(DEMO_USER_ID),
        journalAPI.getAIJournals(DEMO_USER_ID),
      ])
      setUserJournals(user)
      setAIJournals(ai)
    } catch (error) {
      console.error('Failed to load journals:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateJournal = async () => {
    if (!newEntry.trim()) return

    try {
      const tagList = tags.split(',').map(t => t.trim()).filter(t => t)
      await journalAPI.createUserJournal({
        user_id: DEMO_USER_ID,
        content: newEntry,
        tags: tagList.length > 0 ? tagList : undefined,
      })
      setNewEntry('')
      setTags('')
      loadJournals()
    } catch (error) {
      console.error('Failed to create journal:', error)
    }
  }

  return (
    <div className="journal-view">
      <div className="journal-header">
        <h2>Journal</h2>
        <div className="journal-tabs">
          <button
            className={activeTab === 'user' ? 'active' : ''}
            onClick={() => setActiveTab('user')}
          >
            My Journal
          </button>
          <button
            className={activeTab === 'ai' ? 'active' : ''}
            onClick={() => setActiveTab('ai')}
          >
            Tymon's Reflections
          </button>
        </div>
      </div>

      {activeTab === 'user' && (
        <div className="journal-content">
          <div className="new-entry-section">
            <h3>New Entry</h3>
            <textarea
              className="journal-input"
              value={newEntry}
              onChange={(e) => setNewEntry(e.target.value)}
              placeholder="Write your thoughts..."
              rows={6}
            />
            <input
              type="text"
              className="tags-input"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="Tags (comma-separated)"
            />
            <button className="save-button" onClick={handleCreateJournal}>
              Save Entry
            </button>
          </div>

          <div className="entries-section">
            <h3>Your Entries</h3>
            {isLoading ? (
              <p>Loading...</p>
            ) : userJournals.length === 0 ? (
              <div className="empty">
                <div className="empty-state-icon">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" />
                  </svg>
                </div>
                <p>No journal entries yet.</p>
                <p className="empty-hint">Write your first entry above!</p>
              </div>
            ) : (
              userJournals.map((journal) => (
                <JournalEntry key={journal.id} journal={journal} type="user" />
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === 'ai' && (
        <div className="journal-content">
          <div className="ai-journals-info">
            <p>Tymon writes reflections after each conversation to learn and improve.</p>
          </div>
          {isLoading ? (
            <p>Loading...</p>
          ) : aiJournals.length === 0 ? (
            <div className="empty">
              <div className="empty-state-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" />
                </svg>
              </div>
              <p>No AI reflections yet.</p>
              <p className="empty-hint">Start chatting to see Tymon&apos;s thoughts!</p>
            </div>
          ) : (
            aiJournals.map((journal) => (
              <div key={journal.id} className="ai-journal-entry">
                <div className="journal-date">
                  {new Date(journal.created_at).toLocaleString()}
                </div>
                <div className="reflection-section">
                  <h4>Reflection</h4>
                  <p>{journal.reflection}</p>
                </div>
                {journal.learnings.length > 0 && (
                  <div className="learnings-section">
                    <h4>Learnings</h4>
                    <ul>
                      {journal.learnings.map((learning, idx) => (
                        <li key={idx}>{learning}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {journal.questions_raised.length > 0 && (
                  <div className="questions-section">
                    <h4>Questions Asked</h4>
                    <ul>
                      {journal.questions_raised.map((question, idx) => (
                        <li key={idx}>{question}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default JournalView
