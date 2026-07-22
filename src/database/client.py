import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("KEY.env")

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_KEY")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in KEY.env file")

db: Client = create_client(url, key)
