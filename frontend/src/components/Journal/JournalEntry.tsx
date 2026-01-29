import { UserJournal } from '../../services/api'
import './JournalEntry.css'

interface JournalEntryProps {
  journal: UserJournal
  type: 'user'
}

const JournalEntry = ({ journal }: JournalEntryProps) => {
  return (
    <div className="journal-entry">
      <div className="entry-header">
        <div className="entry-date">
          {new Date(journal.created_at).toLocaleString()}
        </div>
        {journal.tags && journal.tags.length > 0 && (
          <div className="entry-tags">
            {journal.tags.map((tag, idx) => (
              <span key={idx} className="tag">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
      <div className="entry-content">{journal.content}</div>
    </div>
  )
}

export default JournalEntry
