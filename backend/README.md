# AI Talk Backend (Tymon API)

## Environment variables (required for deployment)

When deploying to **Vercel** (or any host), set these in **Project → Settings → Environment Variables**:

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL (Dashboard → Project Settings → API) |
| `SUPABASE_KEY` | **Supabase API key**: use **anon (public)** or **service_role** from Dashboard → Project Settings → API. Copy the value exactly (no extra spaces). If you get "Invalid API key" (401), paste the other key. |
| `GEMINI_API_KEY` or `GEMINI_API_KEYS` | Google Gemini API key(s). Use `GEMINI_API_KEYS` for comma-separated multiple keys. |

After adding or changing environment variables on Vercel, **redeploy** the project for them to take effect.

## Local development

1. Copy `.env.example` to `.env` and fill in the same variables.
2. Run the schema in Supabase SQL Editor: see `supabase_schema.sql`.
3. **For pin/delete conversations:** If you already have the base schema, run `supabase_migration_pinned.sql` in Supabase SQL Editor. (Without this, the app still loads but pin/delete will not work.)
4. Start the app: `uvicorn app.main:app --reload` (or use `run.py`).
