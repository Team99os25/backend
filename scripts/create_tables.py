from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment variables")
        return
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Create session_reasons table if it doesn't exist
    try:
        # Using SQL to create the table
        result = supabase.postgrest.rpc(
            "create_session_reasons_table",
            {
                "sql": """
                CREATE TABLE IF NOT EXISTS session_reasons (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
                    reason TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """
            }
        ).execute()
        
        print("Created session_reasons table or it already exists")
    except Exception as e:
        print(f"Error creating session_reasons table: {str(e)}")
    
    print("Database setup complete")

if __name__ == "__main__":
    main()
