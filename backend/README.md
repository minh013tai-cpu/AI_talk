# AI Talk Backend (Tymon API)

## Environment variables (required for deployment)

When deploying to **Vercel** (or any host), set these in **Project → Settings → Environment Variables**:

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/service key (with access to `users`, `conversations`, etc.) |
| `GEMINI_API_KEY` or `GEMINI_API_KEYS` | Google Gemini API key(s). Use `GEMINI_API_KEYS` for comma-separated multiple keys. |

After adding or changing environment variables on Vercel, **redeploy** the project for them to take effect.

## Local development

1. Copy `.env.example` to `.env` and fill in the same variables.
2. Run the schema in Supabase SQL Editor: see `supabase_schema.sql`.
3. Start the app: `uvicorn app.main:app --reload` (or use `run.py`).
