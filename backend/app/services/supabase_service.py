import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase_client: Client = None


def get_supabase_client() -> Client:
    """Get or create Supabase client singleton"""
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = (
            os.getenv("SUPABASE_KEY")
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_SECRET")
        )
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and one of SUPABASE_KEY / SUPABASE_SERVICE_ROLE_KEY / SUPABASE_SECRET must be set"
            )
        _supabase_client = create_client(url, key)
    return _supabase_client


# Demo user ID used by frontend; use a fixed short username to avoid long/duplicate issues
DEMO_USER_ID = "00000000-0000-0000-0000-000000000000"
DEMO_USERNAME = "demo_user"


def ensure_user_exists(user_id: str) -> bool:
    """
    Ensure a user exists in the users table. Create if not exists.
    Returns True if user exists or was created, False on error.
    """
    client = get_supabase_client()
    
    try:
        # Check if user exists
        result = client.table("users").select("id").eq("id", user_id).execute()
        
        if result.data and len(result.data) > 0:
            # User already exists
            return True
        
        # User doesn't exist, create it
        if user_id == DEMO_USER_ID:
            username = DEMO_USERNAME
        else:
            # Use user_id (without hyphens) as username to ensure uniqueness
            username = f"user_{user_id.replace('-', '')}"
        
        user_data = {
            "id": user_id,
            "username": username,
            "settings": {}
        }
        
        try:
            insert_result = client.table("users").insert(user_data).execute()
            
            if insert_result.data:
                return True
            else:
                print(f"Failed to create user {user_id}")
                return False
        except Exception as insert_error:
            # If insert fails due to duplicate username, try with timestamp suffix
            error_str = str(insert_error).lower()
            if "duplicate" in error_str or "unique" in error_str or "violates unique constraint" in error_str:
                # Username conflict, try with timestamp
                from datetime import datetime
                timestamp_suffix = datetime.now().strftime("%Y%m%d%H%M%S%f")[:16]
                username = f"user_{user_id.replace('-', '')[:10]}_{timestamp_suffix}"
                user_data["username"] = username
                
                try:
                    insert_result = client.table("users").insert(user_data).execute()
                    if insert_result.data:
                        return True
                except:
                    pass
            
            # If still fails, check if user was created by another request (race condition)
            # by checking if user_id now exists
            try:
                check_result = client.table("users").select("id").eq("id", user_id).execute()
                if check_result.data and len(check_result.data) > 0:
                    return True
            except:
                pass
            
            print(f"Error creating user {user_id}: {insert_error}")
            return False
            
    except Exception as e:
        # Final fallback: check if user exists (might have been created by another request)
        try:
            check_result = client.table("users").select("id").eq("id", user_id).execute()
            if check_result.data and len(check_result.data) > 0:
                return True
        except:
            pass
        
        print(f"Error ensuring user exists: {e}")
        return False


def init_database():
    """Initialize database tables - run this once to create tables"""
    # Note: In production, use Supabase migrations
    # This is just a helper function for reference
    client = get_supabase_client()
    
    # Tables should be created via Supabase dashboard or migrations
    # This function can be used to verify connection
    try:
        # Test connection
        result = client.table("users").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
