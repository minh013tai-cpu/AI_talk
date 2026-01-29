from app.services.supabase_service import get_supabase_client

def get_db():
    """Dependency for getting Supabase client"""
    return get_supabase_client()
