# Tymon AI Chatbot Platform

A personalized AI chatbot platform featuring Tymon, an AI assistant with human-like communication, long-term memory, critical thinking, and self-reflection capabilities.

## Features

- **Personalized AI Chatbot**: Tymon learns from conversations and remembers important details
- **Long-term Memory**: Intelligent memory system that extracts, scores, and filters important information
- **Critical Thinking**: Tymon can question, challenge, and ask for clarification like a human
- **Journal System**: Both user and AI can write journals for reflection and learning
- **API Integrations**: Gemini AI and Supabase database

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: React + TypeScript with Vite
- **Database**: Supabase (PostgreSQL)
- **AI**: Google Gemini API

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- Supabase account
- Google Gemini API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (already configured in `.env`):
```env
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SECRET=your_supabase_secret
```

5. Set up Supabase database:
   - Go to your Supabase project SQL Editor
   - Run the SQL script from `backend/supabase_schema.sql` to create all tables

6. Run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Project Structure

```
AI_talk/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/                 # API routes
│   │   ├── services/            # Business logic
│   │   ├── models/              # Pydantic models
│   │   └── utils/               # Utilities
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API clients
│   │   └── hooks/               # Custom hooks
│   └── package.json
└── README.md
```

## Usage

1. Start the backend server (port 8000)
2. Start the frontend server (port 5173)
3. Open `http://localhost:5173` in your browser
4. Start chatting with Tymon!

## Features in Detail

### Memory System
- Automatically extracts important information from conversations
- Scores memories by importance (0.0 to 1.0)
- Filters out trivial information
- Retrieves relevant memories during conversations

### Critical Thinking
- Tymon can say "no" and respectfully disagree
- Asks clarifying questions when needed
- Challenges assumptions
- Encourages deeper thinking

### Journal System
- **User Journal**: Write personal thoughts and reflections
- **AI Journal**: Tymon writes self-reflections after each conversation
  - Reflection on the conversation
  - Key learnings
  - Questions raised

## API Endpoints

### Chat
- `POST /api/chat/` - Send a message to Tymon
- `GET /api/chat/history/{user_id}` - Get conversation history

### Memory
- `GET /api/memory/{user_id}` - Get all memories
- `GET /api/memory/{user_id}/relevant` - Get relevant memories for a query
- `DELETE /api/memory/{memory_id}` - Delete a memory

### Journal
- `POST /api/journal/user` - Create user journal entry
- `GET /api/journal/user/{user_id}` - Get user journals
- `GET /api/journal/ai/{user_id}` - Get AI journals
- And more...

## Notes

- Currently uses a demo user ID (`00000000-0000-0000-0000-000000000000`) for testing
- In production, implement proper user authentication
- Memory extraction uses Gemini API for intelligent analysis
- AI journal generation happens asynchronously after each conversation

## License

MIT
