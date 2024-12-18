from supabase import create_client
from dotenv import load_dotenv
import os

# Carica il file .env
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
print(url)
print(key)
