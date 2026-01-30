import { BrowserRouter as Router, Routes, Route, Outlet, Link } from 'react-router-dom'
import ChatInterface from './components/Chat/ChatInterface'
import JournalView from './components/Journal/JournalView'
import MemoryView from './components/Memory/MemoryView'
import BackendHealthBanner from './components/BackendHealthBanner'
import './App.css'

function AppLayout() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Tymon AI</h1>
        <nav>
          <Link to="/">Chat</Link>
          <Link to="/journal">Journal</Link>
          <Link to="/memory">Memories</Link>
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}

function App() {
  return (
    <Router>
      <BackendHealthBanner />
      <Routes>
        <Route path="/" element={<ChatInterface />} />
        <Route element={<AppLayout />}>
          <Route path="/journal" element={<JournalView />} />
          <Route path="/memory" element={<MemoryView />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
