# Setup Guide for Tymon AI Chatbot

## Quick Start

### 0. Chạy toàn bộ (backend + frontend)

Từ thư mục gốc dự án:

```bash
npm install
npm run dev
```

Lệnh này sẽ chạy backend (port 8000) và frontend (port 5173) cùng lúc.

Hoặc chạy riêng từng phần:
- **Backend:** `npm run dev:backend` (hoặc `cd backend && python run.py`)
- **Frontend:** `npm run dev:frontend` (hoặc `cd frontend && npm run dev`)

### 1. Database Setup (Supabase)

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `backend/supabase_schema.sql`
4. Run the SQL script to create all necessary tables

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment variables are already set in .env file
# Verify the API keys are correct

# Run the server
python run.py
# Or:
uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Testing

1. Open `http://localhost:5173` in your browser
2. Start chatting with Tymon!
3. Check the Journal and Memories sections to see how Tymon learns

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure you're in the `backend` directory and virtual environment is activated
- **Supabase connection errors**: Verify your Supabase URL and keys in `.env`
- **Gemini API errors**: Check your Gemini API key is valid

### Frontend Issues

- **API connection errors**: Make sure backend is running on port 8000
- **CORS errors**: Backend CORS is configured for `localhost:5173` and `localhost:3000`

### Database Issues

- Make sure all tables are created using the SQL schema
- Check Supabase project settings and API keys

## Notes

- Currently uses demo user ID (`00000000-0000-0000-0000-000000000000`) for testing
- In production, implement proper authentication
- Memory extraction happens automatically after conversations
- AI journals are generated asynchronously
