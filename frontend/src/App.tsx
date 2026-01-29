import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ChatInterface from './components/Chat/ChatInterface'
import JournalView from './components/Journal/JournalView'
import MemoryView from './components/Memory/MemoryView'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <h1>Tymon AI</h1>
          <nav>
            <a href="/">Chat</a>
            <a href="/journal">Journal</a>
            <a href="/memory">Memories</a>
          </nav>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<ChatInterface />} />
            <Route path="/journal" element={<JournalView />} />
            <Route path="/memory" element={<MemoryView />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
